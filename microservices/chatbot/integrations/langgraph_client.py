"""LangGraph Integration for Chatbot Service

This module builds dynamic LangGraph workflows based on stored chatbot configurations.
It uses ChatbotAgent, ChatbotNode, ChatbotTool, and ChatbotState models to create
customizable conversation graphs.

Supports:
- Agent prompts using variables from state (created by other agents)
- Agent output schemas for structured responses
- Tool variable resolution from state
- Custom pattern-based variable extraction
- One-line Python script execution for dynamic configuration
"""
from typing import TypedDict, Annotated, List, Optional, Dict, Any, Literal, Union
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from sqlalchemy.orm import Session
import json
import uuid
import re
from datetime import datetime


from chatbot.core.config import settings
from chatbot.modules.chatbot_agent.model import ChatbotAgent
from chatbot.modules.chatbot_node.model import ChatbotNode
from chatbot.modules.chatbot_tool.model import ChatbotTool
from chatbot.modules.chatbot_state.model import ChatbotState
from chatbot.modules.conversation.model import Conversation
from chatbot.modules.chat_message.model import ChatMessage


class AgentState(TypedDict):
    """State for LangGraph workflow - matches ChatbotState model"""
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]
    current_user_id: Optional[str]
    conversation_id: Optional[int]
    chatbot_id: Optional[int]
    context: Optional[Dict[str, Any]]
    current_node: Optional[str]
    db_session: Optional[Session]
    active_agents: Optional[List[Dict[str, Any]]]
    available_tools: Optional[List[Dict[str, Any]]]


def extract_variables_from_state(state: Dict[str, Any], pattern: str) -> Dict[str, Any]:
    """Extract variables from state based on a regex pattern.
    
    Args:
        state: The current agent state containing context and messages
        pattern: Regex pattern to match variable names (e.g., r'\$\{(\w+)\}' or r'{{(\w+)}}')
    
    Returns:
        Dictionary of variable names to their values found in state
    """
    variables = {}
    
    # Search in context
    if state.get("context"):
        for key, value in state["context"].items():
            if re.match(pattern, f"${{{key}}}") or re.match(pattern, f"{{{{{key}}}}}"):
                variables[key] = value
    
    # Also check for direct pattern matches in context values
    if pattern:
        try:
            compiled_pattern = re.compile(pattern)
            # Search in context string representations
            if state.get("context"):
                for key, value in state["context"].items():
                    if isinstance(value, str):
                        matches = compiled_pattern.findall(value)
                        for match in matches:
                            variables[match] = value
            
            # Search in recent messages for extracted variables
            for msg in state.get("messages", [])[-5:]:
                if hasattr(msg, 'content') and isinstance(msg.content, str):
                    matches = compiled_pattern.findall(msg.content)
                    for match in matches:
                        if match not in variables:
                            variables[match] = match
        except re.error:
            pass  # Invalid regex pattern, skip
    
    return variables


def resolve_variables_in_text(text: str, state: Dict[str, Any]) -> str:
    """Resolve variable placeholders in text using values from state.
    
    Supports multiple placeholder formats:
    - ${expression} - Python expressions (including f-strings with nested braces)
    - {{variable_name}} - Simple variable substitution
    - {variable_name} - Simple variable substitution
    
    Args:
        text: Text containing variable placeholders or Python expressions
        state: The current agent state
    
    Returns:
        Text with variables replaced by their values from state
    
    Examples:
        - "Hello ${user}" -> "Hello John" (if user=John in context)
        - "hey ${_ctx.get('user') if True else _ctx.get('name')}" -> evaluates the expression
        - "${f'you can do {job}'}" -> evaluates the f-string
        - "Bearer {token_key}" -> "Bearer abc123" (if token_key=abc123)
        - '{"obj": ${int(var.get("num"))}}' -> '{"obj": 42}' (if var={"num": 42})
    """
    if not text:
        return text
    
    resolved = text
    
    # Extract all potential variables from context
    context_vars = state.get("context", {})
    
    # Create a shortcut _ctx for context access in expressions
    exec_env = {"_ctx": context_vars, "state": state, "json": json, "datetime": datetime}
    # Also add individual context variables for direct access
    exec_env.update(context_vars)
    
    # Handle Python expressions in ${...} format with support for nested braces
    # This pattern finds ${...} and properly handles nested braces inside
    def find_and_replace_expressions(text):
        result = []
        i = 0
        while i < len(text):
            # Look for ${
            if text[i:i+2] == '${':
                # Find matching closing brace
                start = i + 2
                brace_count = 1
                j = start
                while j < len(text) and brace_count > 0:
                    if text[j] == '{':
                        brace_count += 1
                    elif text[j] == '}':
                        brace_count -= 1
                    j += 1
                
                if brace_count == 0:
                    # Found complete expression
                    expr = text[start:j-1].strip()
                    try:
                        # Try to evaluate as Python expression
                        eval_result = eval(expr, exec_env, {})
                        result.append(str(eval_result))
                    except Exception:
                        # If evaluation fails, treat as simple variable lookup
                        if expr in exec_env:
                            result.append(str(exec_env[expr]))
                        else:
                            result.append(text[i:j])  # Keep original
                    i = j
                else:
                    result.append(text[i])
                    i += 1
            else:
                result.append(text[i])
                i += 1
        
        return ''.join(result)
    
    resolved = find_and_replace_expressions(resolved)
    
    # Replace remaining {{variable}} format
    for var_name, var_value in context_vars.items():
        placeholder = f"{{{{{var_name}}}}}"
        if placeholder in resolved:
            resolved = resolved.replace(placeholder, str(var_value))
        
        # Replace {variable} format (simple substitution, not expressions)
        placeholder = f"{{{var_name}}}"
        if placeholder in resolved:
            resolved = resolved.replace(placeholder, str(var_value))
    
    return resolved


def execute_dynamic_script(script: str, state: Dict[str, Any]) -> Any:
    """Execute a one-line Python script with access to state variables.
    
    Args:
        script: One-line Python script to execute
        state: The current agent state (available as 'state' variable in script)
    
    Returns:
        Result of the script execution
    
    Example scripts:
        - "state['context'].get('user_name', 'User')"
        - "len(state['messages'])"
        - "state['context']['order_id'] if 'order_id' in state['context'] else None"
        - "'Premium' if state['context'].get('tier') == 'premium' else 'Standard'"
    """
    if not script:
        return None
    
    try:
        # Create a safe execution environment
        exec_globals = {"state": state, "json": json, "datetime": datetime}
        result = eval(script, exec_globals, {})
        return result
    except Exception as e:
        return f"[Script execution error: {str(e)}]"


def apply_output_schema(response: Any, schema: Dict[str, Any]) -> Dict[str, Any]:
    """Apply output schema to agent response.
    
    Args:
        response: The raw response from the agent
        schema: JSON schema defining the expected output structure
    
    Returns:
        Response formatted according to the schema
    """
    if not schema:
        return response
    
    try:
        # If response is already a dict, validate/transform against schema
        if isinstance(response, dict):
            # Simple schema validation - ensure required fields exist
            required_fields = schema.get("required", [])
            properties = schema.get("properties", {})
            
            result = {}
            for field, field_schema in properties.items():
                if field in response:
                    result[field] = response[field]
                elif field in required_fields:
                    # Use default if available
                    result[field] = field_schema.get("default", None)
            
            return result
        
        # If response is a string, try to parse as JSON
        if isinstance(response, str):
            try:
                parsed = json.loads(response)
                return apply_output_schema(parsed, schema)
            except json.JSONDecodeError:
                # Return as-is if not valid JSON
                return {"output": response}
        
        return {"output": response}
    
    except Exception as e:
        return {"output": response, "_schema_error": str(e)}


class LangGraphChatbot:
    """Chatbot using LangGraph for stateful conversations with dynamic graph building"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session
        self.graph = None
        self.checkpointer = MemorySaver()
    
    def _get_llm(self, model_name: str = "gpt-4o-mini", temperature: float = 0.7):
        """Get LLM instance based on agent configuration"""
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=settings.OPENAI_API_KEY
        )
    
    def _load_chatbot_config(self, chatbot_id: int) -> Dict[str, Any]:
        """Load chatbot configuration from database including agents, nodes, and tools"""
        if not self.db_session:
            raise ValueError("Database session required")
        
        # Load agents
        agents = self.db_session.query(ChatbotAgent).filter(
            ChatbotAgent.chatbot_id == chatbot_id,
            ChatbotAgent.is_active == True
        ).order_by(ChatbotAgent.priority).all()
        
        # Load nodes
        nodes = self.db_session.query(ChatbotNode).filter(
            ChatbotNode.chatbot_id == chatbot_id,
            ChatbotNode.is_active == True
        ).all()
        
        # Load tools
        tools = self.db_session.query(ChatbotTool).filter(
            ChatbotTool.chatbot_id == chatbot_id,
            ChatbotTool.is_active == True
        ).all()
        
        return {
            "agents": agents,
            "nodes": nodes,
            "tools": tools
        }
    
    def _create_agent_node(self, agent: ChatbotAgent):
        """Create a node function for an agent"""
        async def agent_node(state: AgentState) -> AgentState:
            llm = self._get_llm(agent.model_name, agent.temperature)
            
            # Build system prompt with variable resolution
            system_content = agent.system_prompt or "You are a helpful AI assistant."
            
            # First, try to execute dynamic script if available
            if agent.dynamic_script:
                script_result = execute_dynamic_script(agent.dynamic_script, state)
                if script_result:
                    # Append script result to system prompt or use as additional context
                    system_content = f"{system_content}\n\nDynamic Context: {script_result}"
            
            # Resolve variables in the system prompt (supports Python expressions in ${...})
            resolved_system_content = resolve_variables_in_text(system_content, state)
            
            # Extract variables based on agent's input_variables list or variable_pattern
            if agent.input_variables:
                # Use explicit input_variables list
                context_vars = state.get("context", {})
                extracted_vars = {k: v for k, v in context_vars.items() if k in agent.input_variables}
                if extracted_vars:
                    vars_context = "\n".join([f"{k}: {v}" for k, v in extracted_vars.items()])
                    resolved_system_content = f"{resolved_system_content}\n\nAvailable Variables:\n{vars_context}"
            elif agent.variable_pattern:
                # Use regex pattern for variable extraction
                extracted_vars = extract_variables_from_state(state, agent.variable_pattern)
                if extracted_vars:
                    vars_context = "\n".join([f"{k}: {v}" for k, v in extracted_vars.items()])
                    resolved_system_content = f"{resolved_system_content}\n\nAvailable Variables:\n{vars_context}"
            
            messages = [SystemMessage(content=resolved_system_content)] + state["messages"]
            
            # Apply output schema if defined
            if agent.output_schema:
                # Instruct LLM to follow the output schema
                schema_instruction = f"\n\nPlease format your response according to this schema: {json.dumps(agent.output_schema)}"
                messages[-1] = HumanMessage(content=state["messages"][-1].content + schema_instruction)
            
            # Call LLM
            response = await llm.ainvoke(messages)
            
            # Apply output schema to the response
            if agent.output_schema:
                structured_response = apply_output_schema(response.content, agent.output_schema)
                response.content = json.dumps(structured_response)
            
            # Store message in database if session available
            if state.get("db_session") and state.get("conversation_id"):
                self._store_message(
                    db=state["db_session"],
                    conversation_id=state["conversation_id"],
                    role="assistant",
                    content=response.content,
                    agent_name=agent.name,
                    node_name=agent.role
                )
            
            # Update context with agent's output
            new_context = state.get("context", {}).copy()
            
            # Store in default location
            new_context[f"last_agent_{agent.role}"] = response.content
            
            # Also store in specified output_variables if defined
            if agent.output_variables:
                for var_name in agent.output_variables:
                    new_context[var_name] = response.content
            
            return {
                "messages": [response],
                "current_node": agent.role,
                "context": new_context
            }
        
        return agent_node
    
    def _create_tool_node(self, tool: ChatbotTool):
        """Create a node function for a tool"""
        async def tool_node(state: AgentState) -> AgentState:
            # Execute tool logic with variable resolution
            tool_result = await self._execute_tool(tool, state)
            
            # Store tool result as message
            if state.get("db_session") and state.get("conversation_id"):
                self._store_message(
                    db=state["db_session"],
                    conversation_id=state["conversation_id"],
                    role="tool",
                    content=str(tool_result),
                    tool_call_id=tool.name
                )
            
            # Update context with tool output
            new_context = state.get("context", {}).copy()
            
            # Store in default location
            new_context[f"last_tool_{tool.name}"] = str(tool_result)
            
            # Also store in specified output_variables if defined
            if tool.output_variables:
                for var_name in tool.output_variables:
                    new_context[var_name] = tool_result
            
            return {
                "messages": [ToolMessage(content=str(tool_result), tool_call_id=tool.name)],
                "current_node": f"tool_{tool.name}",
                "context": new_context
            }
        
        return tool_node
    
    async def _execute_tool(self, tool: ChatbotTool, state: AgentState) -> Any:
        """Execute a tool based on its configuration with variable resolution"""
        tool_config = tool.tool_config or {}
        
        # Resolve variables in tool configuration using dynamic_script or variable_pattern
        if tool.dynamic_script:
            # Execute one-line Python script to get dynamic configuration
            script_result = execute_dynamic_script(tool.dynamic_script, state)
            if script_result and isinstance(script_result, dict):
                tool_config = {**tool_config, **script_result}
        
        # Resolve variables in headers, body_template, url using state context
        if tool.url:
            resolved_url = resolve_variables_in_text(tool.url, state)
        else:
            resolved_url = None
        
        if tool.headers:
            resolved_headers = {}
            for key, value in tool.headers.items():
                if isinstance(value, str):
                    resolved_headers[key] = resolve_variables_in_text(value, state)
                else:
                    resolved_headers[key] = value
        else:
            resolved_headers = {}
        
        if tool.body_template:
            resolved_body = resolve_variables_in_text(tool.body_template, state)
        else:
            resolved_body = None
        
        if tool.tool_type == "builtin":
            # Handle builtin tools
            if tool.name == "search":
                # Placeholder for search functionality
                return {"result": "Search results placeholder"}
            elif tool.name == "calculator":
                # Placeholder for calculator
                return {"result": "Calculator result placeholder"}
        
        elif tool.tool_type == "api":
            # Call external API with resolved variables
            import httpx
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        resolved_url or tool_config.get("endpoint", ""),
                        json={"state": state, "body": resolved_body} if resolved_body else {"state": state},
                        headers=resolved_headers or tool_config.get("headers", {})
                    )
                    return response.json()
            except Exception as e:
                return {"error": f"API call failed: {str(e)}"}
        
        elif tool.tool_type == "code" and tool.code_content:
            # Execute custom Python code with access to state
            try:
                exec_globals = {"state": state, "json": json, "datetime": datetime, "httpx": __import__('httpx')}
                result = eval(tool.code_content, exec_globals, {})
                return result
            except Exception as e:
                return {"error": f"Code execution failed: {str(e)}"}
        
        return {"result": f"Tool {tool.name} executed", "config_used": tool_config}
    
    def _store_message(
        self,
        db: Session,
        conversation_id: int,
        role: str,
        content: str,
        agent_name: Optional[str] = None,
        node_name: Optional[str] = None,
        tool_call_id: Optional[str] = None,
        total_tokens: int = 0
    ):
        """Store message in database"""
        message = ChatMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            agent_name=agent_name,
            node_name=node_name,
            tool_call_id=tool_call_id,
            total_tokens=total_tokens
        )
        db.add(message)
        db.commit()
        
        # Update conversation message count
        conversation = db.query(Conversation).get(conversation_id)
        if conversation:
            conversation.message_count += 1
            conversation.last_message_at = datetime.utcnow()
            db.commit()
    
    def _save_state(self, db: Session, conversation_id: int, chatbot_id: int, state: AgentState):
        """Save or update chatbot state in database"""
        existing_state = db.query(ChatbotState).filter(
            ChatbotState.conversation_id == conversation_id
        ).first()
        
        state_data = {
            "messages": [{"type": type(m).__name__, "content": m.content} for m in state.get("messages", [])],
            "current_node": state.get("current_node"),
            "context": state.get("context")
        }
        
        if existing_state:
            existing_state.state_data = state_data
            existing_state.current_node = state.get("current_node")
            existing_state.updated_at = datetime.utcnow()
        else:
            new_state = ChatbotState(
                conversation_id=conversation_id,
                chatbot_id=chatbot_id,
                state_data=state_data,
                current_node=state.get("current_node"),
                message_count=len(state.get("messages", []))
            )
            db.add(new_state)
        
        db.commit()
    
    def _build_graph(self, chatbot_id: int) -> StateGraph:
        """Build LangGraph workflow based on stored configuration"""
        config = self._load_chatbot_config(chatbot_id)
        
        workflow = StateGraph(AgentState)
        
        agents = config["agents"]
        nodes = config["nodes"]
        tools = config["tools"]
        
        # Add agent nodes
        for agent in agents:
            workflow.add_node(agent.role, self._create_agent_node(agent))
        
        # Add tool nodes
        for tool in tools:
            workflow.add_node(f"tool_{tool.name}", self._create_tool_node(tool))
        
        # Add entry point - use first agent or default to first node
        entry_point = None
        if agents:
            entry_point = agents[0].role
        elif nodes:
            entry_node = next((n for n in nodes if n.is_entry_point), nodes[0])
            entry_point = entry_node.node_name
        
        if entry_point:
            workflow.set_entry_point(entry_point)
        
        # Add edges based on node connections
        for node in nodes:
            if node.edges:
                for edge in node.edges:
                    target = edge.get("to")
                    condition = edge.get("condition")
                    
                    if condition:
                        # Conditional edge
                        workflow.add_conditional_edges(
                            node.node_name,
                            lambda x: target,
                            [target]
                        )
                    else:
                        # Regular edge
                        workflow.add_edge(node.node_name, target)
        
        # If no custom nodes, create default flow
        if not nodes:
            if agents:
                # Chain agents in priority order
                for i in range(len(agents) - 1):
                    workflow.add_edge(agents[i].role, agents[i+1].role)
                
                # Last agent goes to END
                workflow.add_edge(agents[-1].role, END)
            else:
                # Default single node flow
                workflow.add_node("default", self._default_node)
                workflow.set_entry_point("default")
                workflow.add_edge("default", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    async def _default_node(self, state: AgentState) -> AgentState:
        """Default node when no agents/nodes configured"""
        llm = self._get_llm()
        response = await llm.ainvoke(state["messages"])
        return {"messages": [response]}
    
    async def process_message(
        self,
        user_message: str,
        chatbot_id: int,
        conversation_id: Optional[int] = None,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a message through the LangGraph workflow"""
        if not self.db_session:
            raise ValueError("Database session required")
        
        # Build or rebuild graph
        if self.graph is None:
            self.graph = self._build_graph(chatbot_id)
        
        # Create conversation if not provided
        if not conversation_id:
            conversation = Conversation(
                chatbot_id=chatbot_id,
                user_id=user_id or 0,
                title=f"Conversation {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                session_id=str(uuid.uuid4())
            )
            self.db_session.add(conversation)
            self.db_session.commit()
            conversation_id = conversation.id
        
        # Load conversation history
        messages = self.db_session.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).order_by(ChatMessage.created_at).limit(10).all()
        
        # Convert to LangChain messages
        langchain_messages = []
        for msg in messages:
            if msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                langchain_messages.append(AIMessage(content=msg.content))
            elif msg.role == "system":
                langchain_messages.append(SystemMessage(content=msg.content))
            elif msg.role == "tool":
                langchain_messages.append(ToolMessage(content=msg.content, tool_call_id=msg.tool_call_id or ""))
        
        # Add new user message
        langchain_messages.append(HumanMessage(content=user_message))
        
        # Store user message
        self._store_message(
            db=self.db_session,
            conversation_id=conversation_id,
            role="user",
            content=user_message
        )
        
        # Prepare initial state
        initial_state = AgentState(
            messages=langchain_messages,
            current_user_id=user_id,
            conversation_id=conversation_id,
            chatbot_id=chatbot_id,
            context=context or {},
            current_node=None,
            db_session=self.db_session,
            active_agents=None,
            available_tools=None
        )
        
        # Run graph
        config = {"configurable": {"thread_id": str(conversation_id)}}
        result = await self.graph.ainvoke(initial_state, config=config)
        
        # Save state
        self._save_state(self.db_session, conversation_id, chatbot_id, result)
        
        # Get last AI message
        ai_response = ""
        for msg in reversed(result.get("messages", [])):
            if isinstance(msg, AIMessage):
                ai_response = msg.content
                break
        
        return {
            "response": ai_response,
            "conversation_id": conversation_id,
            "messages": result.get("messages", [])
        }
    
    async def chat_stream(
        self,
        user_message: str,
        chatbot_id: int,
        conversation_id: Optional[int] = None,
        user_id: Optional[str] = None
    ):
        """Stream chat response (placeholder for streaming implementation)"""
        result = await self.process_message(
            user_message=user_message,
            chatbot_id=chatbot_id,
            conversation_id=conversation_id,
            user_id=user_id
        )
        
        # Yield response character by character (simplified streaming)
        for char in result["response"]:
            yield char


# Factory function to create chatbot instance with DB session
def get_langgraph_chatbot(db_session: Session) -> LangGraphChatbot:
    """Create LangGraph chatbot instance with database session"""
    return LangGraphChatbot(db_session=db_session)
