# Chatbot Integration Updates - Variable Resolution & Python Expressions

## Overview
Updated chatbot models and integrations to support:
1. **Python expressions in prompts and tool configurations** - Any user input can contain executable one-line Python commands
2. **Input/output variables for agents and tools** - Control where data comes from and where results are stored
3. **Enhanced variable resolution** - Support for `${expression}`, `{variable}`, and `{{variable}}` formats

## Files Modified

### 1. Database Models

#### `/workspace/microservices/chatbot/modules/chatbot_agent/model.py`
Added columns to `ChatbotAgent`:
- `input_variables` (JSON): List of variable names to extract from state for this agent
- `output_variables` (JSON): List of variable names where agent output should be stored

#### `/workspace/microservices/chatbot/modules/chatbot_tool/model.py`
Added columns to `ChatbotTool`:
- `input_variables` (JSON): List of variable names to extract from state for this tool
- `output_variables` (JSON): List of variable names where tool output should be stored

### 2. Pydantic Schemas

#### `/workspace/microservices/chatbot/modules/chatbot_agent/schemas.py`
Updated schemas (`ChatbotAgentCreate`, `ChatbotAgentUpdate`, `ChatbotAgentResponse`):
- Added `input_variables: Optional[List[str]]`
- Added `output_variables: Optional[List[str]]`
- Added `variable_pattern: Optional[str]` to response schema
- Added `dynamic_script: Optional[str]` to response schema

#### `/workspace/microservices/chatbot/modules/chatbot_tool/schemas.py`
Updated schemas (`ChatbotToolCreate`, `ChatbotToolUpdate`, `ChatbotToolResponse`):
- Added `input_variables: Optional[List[str]]`
- Added `output_variables: Optional[List[str]]`
- Added `variable_pattern: Optional[str]` to response schema
- Added `dynamic_script: Optional[str]` to response schema

### 3. LangGraph Integration

#### `/workspace/microservices/chatbot/integrations/langgraph_client.py`

**Enhanced `resolve_variables_in_text()` function:**
- Now supports Python expressions inside `${...}` with nested braces
- Handles f-strings like `${f'you can do {job}'}` 
- Supports conditional expressions like `${_ctx.get('user') if True else _ctx.get('name')}`
- Simple variable substitution with `{variable}` or `{{variable}}`
- Provides `_ctx` shortcut for context access in expressions

**Updated `_create_agent_node()`:**
- Uses `input_variables` list (preferred) or falls back to `variable_pattern` regex
- Stores agent output in `output_variables` locations if specified
- Resolves Python expressions in system prompts before sending to LLM

**Updated `_create_tool_node()`:**
- Stores tool output in `output_variables` locations if specified
- Enables downstream nodes to access tool results via named variables

**Updated `_execute_tool()`:**
- Resolves Python expressions in URLs, headers, and body templates
- Example: `request_body: {"obj1": ${int(var.get('int_obj1'))}}`
- Example: `header auth: 'Bearer {token_key}'`

## Usage Examples

### Agent Prompt with Python Expressions
```python
# Agent configuration
agent = ChatbotAgent(
    name="greeter",
    role="greeter",
    system_prompt="hey ${_ctx.get('user') if True else _ctx.get('name')} what do you want? ${f'you can do {job}'}",
    input_variables=["user", "name", "job"],  # Explicit variables to extract
    output_variables=["greeting_response"]    # Where to store the output
)

# Before: "hey ${_ctx.get('user') if True else _ctx.get('name')} what do you want? ${f'you can do {job}'}"
# After:  "hey Alice what do you want? you can do engineer"
```

### Tool Configuration with Python Expressions
```python
# Tool with dynamic request body
tool = ChatbotTool(
    name="api_call",
    tool_type="api",
    url="https://api.example.com/data",
    headers={"Authorization": "Bearer {token_key}"},
    body_template='{"obj1": ${int(var.get("int_obj1"))}}',
    input_variables=["token_key", "var"],
    output_variables=["api_result"]
)

# Before body: '{"obj1": ${int(var.get("int_obj1"))}}'
# After body:  '{"obj1": 42}'

# Before header: 'Bearer {token_key}'
# After header:  'Bearer abc123'
```

### State Flow Example
```python
# Initial state
state = {
    "context": {
        "user": "Alice",
        "job": "engineer",
        "var": {"int_obj1": "42"},
        "token_key": "abc123"
    }
}

# Agent 1 runs, stores output in "research_result"
agent1.output_variables = ["research_result"]
# state.context["research_result"] = "...research data..."

# Agent 2 uses result from Agent 1
agent2.input_variables = ["research_result"]
# Agent 2 prompt can use ${research_result}
```

## Key Features

1. **Executable Prompts**: Any text field can contain Python expressions in `${...}`
2. **Safe Execution**: Expressions run with limited context (`_ctx`, `state`, `json`, `datetime`)
3. **Nested Braces**: F-strings and complex expressions work correctly
4. **Explicit Variable Control**: `input_variables` and `output_variables` provide clear data flow
5. **Backward Compatible**: Existing `variable_pattern` and `dynamic_script` still work

## Security Note
Expressions are evaluated using Python's `eval()` with a restricted global environment. Only these are available:
- `_ctx`: Shortcut to state context
- `state`: Full state dictionary  
- `json`: JSON module
- `datetime`: Datetime module
- Individual context variables

Avoid exposing sensitive operations in user-configurable expressions.
