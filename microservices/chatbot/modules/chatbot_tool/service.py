"""Service layer for ChatbotTool business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List, Dict, Any
import re
import httpx
import json
from datetime import datetime

from modules.chatbot_tool.model import ChatbotTool, HttpMethod
from modules.chatbot_tool.schemas import ChatbotToolCreate, ChatbotToolUpdate


class SafeEnvironment:
    """Restricted execution environment for user code."""
    
    # Restricted builtins - only allow safe operations
    SAFE_BUILTINS = {
        'abs': abs,
        'all': all,
        'any': any,
        'bool': bool,
        'chr': chr,
        'dict': dict,
        'enumerate': enumerate,
        'float': float,
        'int': int,
        'len': len,
        'list': list,
        'max': max,
        'min': min,
        'ord': ord,
        'pow': pow,
        'range': range,
        'reversed': reversed,
        'round': round,
        'set': set,
        'sorted': sorted,
        'str': str,
        'sum': sum,
        'tuple': tuple,
        'zip': zip,
        'True': True,
        'False': False,
        'None': None,
    }
    
    @staticmethod
    def execute(code: str, variables: Dict[str, Any]) -> Any:
        """Execute code in a restricted environment."""
        # Create restricted globals
        restricted_globals = {
            '__builtins__': SafeEnvironment.SAFE_BUILTINS,
            '__name__': '__restricted__',
            '__doc__': None,
        }
        
        # Add variables to locals
        restricted_locals = variables.copy()
        
        try:
            # Compile and execute the code
            exec(code, restricted_globals, restricted_locals)
            # Return result if 'result' variable exists
            return restricted_locals.get('result', None)
        except Exception as e:
            raise RuntimeError(f"Code execution failed: {str(e)}")


class VariableResolver:
    """Resolve variables from state using patterns and scripts."""
    
    @staticmethod
    def extract_variables(state: Dict[str, Any], pattern: str) -> Dict[str, Any]:
        """Extract variables from state using regex pattern."""
        if not pattern:
            return {}
        
        try:
            compiled_pattern = re.compile(pattern)
            matches = compiled_pattern.search(str(state))
            if matches:
                return matches.groupdict()
            return {}
        except Exception:
            return {}
    
    @staticmethod
    def execute_dynamic_script(script: str, state: Dict[str, Any]) -> Any:
        """Execute one-line Python script with state variables."""
        if not script:
            return None
        
        try:
            return SafeEnvironment.execute(script, state)
        except Exception as e:
            raise RuntimeError(f"Dynamic script execution failed: {str(e)}")
    
    @staticmethod
    def resolve_template(template: str, state: Dict[str, Any]) -> str:
        """Replace {variable} placeholders in template with state values."""
        if not template:
            return template
        
        def replace_var(match):
            var_name = match.group(1)
            return str(state.get(var_name, match.group(0)))
        
        return re.sub(r'\{(\w+)\}', replace_var, template)


class ChatbotToolService:
    """Service layer for ChatbotTool business logic."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.resolver = VariableResolver()
    
    async def create_item(self, item_data: ChatbotToolCreate) -> ChatbotTool:
        """Create a new chatbot_tool."""
        tool = ChatbotTool(**item_data.model_dump())
        self.db.add(tool)
        await self.db.commit()
        await self.db.refresh(tool)
        return tool
    
    async def get_item(self, item_id: int) -> Optional[ChatbotTool]:
        """Get chatbot_tool by ID."""
        result = await self.db.execute(select(ChatbotTool).where(ChatbotTool.id == item_id))
        return result.scalar_one_or_none()
    
    async def list_items(self, chatbot_id: Optional[int] = None) -> List[ChatbotTool]:
        """List all items, optionally filtered by chatbot_id."""
        query = select(ChatbotTool)
        if chatbot_id:
            query = query.where(ChatbotTool.chatbot_id == chatbot_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_item(self, item_id: int, item_data: ChatbotToolUpdate) -> Optional[ChatbotTool]:
        """Update chatbot_tool."""
        tool = await self.get_item(item_id)
        if not tool:
            return None
        
        update_data = {k: v for k, v in item_data.model_dump().items() if v is not None}
        for key, value in update_data.items():
            setattr(tool, key, value)
        
        await self.db.commit()
        await self.db.refresh(tool)
        return tool
    
    async def delete_item(self, item_id: int) -> bool:
        """Delete a chatbot_tool."""
        tool = await self.get_item(item_id)
        if not tool:
            return False
        
        await self.db.delete(tool)
        await self.db.commit()
        return True
    
    async def execute_tool(
        self, 
        tool_id: int, 
        state: Dict[str, Any],
        input_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a tool with given state and input data."""
        tool = await self.get_item(tool_id)
        if not tool or not tool.is_active:
            raise ValueError(f"Tool {tool_id} not found or inactive")
        
        # Merge state with input data
        context = {**state, **(input_data or {})}
        
        # Resolve dynamic configurations
        if tool.dynamic_script:
            dynamic_result = self.resolver.execute_dynamic_script(tool.dynamic_script, context)
            if dynamic_result:
                context.update(dynamic_result if isinstance(dynamic_result, dict) else {'result': dynamic_result})
        
        if tool.variable_pattern:
            extracted = self.resolver.extract_variables(context, tool.variable_pattern)
            context.update(extracted)
        
        # Execute based on tool type
        if tool.is_code and tool.code_content:
            # Execute custom code
            result = SafeEnvironment.execute(tool.code_content, context)
            return {'result': result, 'tool_id': tool_id}
        
        elif tool.tool_type == 'api' and tool.url:
            # Execute HTTP request
            url = self.resolver.resolve_template(tool.url, context)
            
            headers = tool.headers or {}
            if isinstance(headers, dict):
                headers = {k: self.resolver.resolve_template(str(v), context) for k, v in headers.items()}
            
            body = None
            if tool.body_template:
                body_str = self.resolver.resolve_template(tool.body_template, context)
                try:
                    body = json.loads(body_str)
                except json.JSONDecodeError:
                    body = body_str
            
            async with httpx.AsyncClient(timeout=tool.timeout_seconds) as client:
                method = tool.method.value if isinstance(tool.method, HttpMethod) else tool.method
                response = await client.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    json=body if isinstance(body, (dict, list)) else None,
                    content=body if isinstance(body, str) else None,
                )
                
                try:
                    response_data = response.json()
                except json.JSONDecodeError:
                    response_data = {'text': response.text}
                
                return {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'data': response_data,
                    'tool_id': tool_id,
                }
        
        else:
            raise ValueError(f"Unsupported tool type: {tool.tool_type}")
