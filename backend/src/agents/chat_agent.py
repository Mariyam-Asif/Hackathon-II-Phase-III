import asyncio
import json
from typing import Dict, Any, List
from pydantic import BaseModel
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

# Import the MCP tools
from agents.tools.add_task import add_task_tool, AddTaskInput
from agents.tools.list_tasks import list_tasks_tool, ListTasksInput
from agents.tools.complete_task import complete_task_tool, CompleteTaskInput
from agents.tools.update_task import update_task_tool, UpdateTaskInput
from agents.tools.delete_task import delete_task_tool, DeleteTaskInput

load_dotenv()

# Initialize OpenAI client lazily or with a check
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    client = AsyncOpenAI(api_key=openai_api_key)
else:
    # We'll set client to None and check it inside the methods
    client = None
    print("Warning: OPENAI_API_KEY not found. Chat functionality will be disabled.")


class AgentRequest(BaseModel):
    user_message: str
    user_id: str
    conversation_history: List[Dict[str, str]] = []


class AgentResponse(BaseModel):
    response_text: str
    tool_calls: List[Dict[str, Any]]
    success: bool


class ChatAgent:
    def __init__(self):
        # Define the available tools for the agent
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Add a new task for the user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "The title of the task"},
                            "description": {"type": "string", "description": "Detailed description of the task"},
                            "priority": {"type": "string", "description": "Priority of the task: low, medium, or high", "default": "medium"}
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "List all tasks for the user",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Mark a task as completed for the user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string", "description": "The ID of the task to complete"}
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update an existing task for the user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string", "description": "The ID of the task to update"},
                            "title": {"type": "string", "description": "New title for the task"},
                            "description": {"type": "string", "description": "New description for the task"},
                            "status": {"type": "string", "description": "New status: pending, in_progress, or completed"},
                            "priority": {"type": "string", "description": "New priority: low, medium, or high"}
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Delete a task for the user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string", "description": "The ID of the task to delete"}
                        },
                        "required": ["task_id"]
                    }
                }
            }
        ]

    async def process_request(self, request: AgentRequest) -> AgentResponse:
        """
        Process a user request through the AI agent and return a response.

        Args:
            request: Contains user message, user ID, and conversation history

        Returns:
            AgentResponse with response text, tool calls, and success status
        """
        if client is None:
            return AgentResponse(
                response_text="Error: OpenAI API key is not configured. Please add OPENAI_API_KEY to environment variables in Hugging Face Space Secrets.",
                tool_calls=[],
                success=False
            )

        try:
            # Prepare the messages for the OpenAI API
            messages = []

            # Add system message to define agent behavior
            messages.append({
                "role": "system",
                "content": """You are an AI task management assistant. Your job is to interpret natural language user requests and map them to appropriate task management operations. You must:
                1. Only perform operations through the available tools
                2. Always respect the user's identity and only access their tasks
                3. Return clear, helpful responses to the user
                4. If a user asks to see their tasks, use the list_tasks tool
                5. If a user wants to add a task, use the add_task tool
                6. If a user wants to complete a task, use the complete_task tool
                7. If a user wants to update a task, use the update_task tool
                8. If a user wants to delete a task, use the delete_task tool
                9. Always use the user_id provided in the request
                10. Never fabricate task data or infer task IDs"""
            })

            # Add conversation history if available
            for msg in request.conversation_history:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

            # Add the current user message
            messages.append({
                "role": "user",
                "content": request.user_message
            })

            # Call the OpenAI API with function calling
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )

            # Process the response
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # If there are tool calls, execute them
            if tool_calls:
                tool_results = []

                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # Execute the appropriate tool based on the function name
                    if function_name == "add_task":
                        input_data = AddTaskInput(user_id=request.user_id, **function_args)
                        result = await add_task_tool(input_data)
                        tool_results.append({
                            "tool_call_id": tool_call.id,
                            "result": result
                        })

                    elif function_name == "list_tasks":
                        input_data = ListTasksInput(user_id=request.user_id)
                        result = await list_tasks_tool(input_data)
                        tool_results.append({
                            "tool_call_id": tool_call.id,
                            "result": result
                        })

                    elif function_name == "complete_task":
                        input_data = CompleteTaskInput(user_id=request.user_id, **function_args)
                        result = await complete_task_tool(input_data)
                        tool_results.append({
                            "tool_call_id": tool_call.id,
                            "result": result
                        })

                    elif function_name == "update_task":
                        input_data = UpdateTaskInput(user_id=request.user_id, **function_args)
                        result = await update_task_tool(input_data)
                        tool_results.append({
                            "tool_call_id": tool_call.id,
                            "result": result
                        })

                    elif function_name == "delete_task":
                        input_data = DeleteTaskInput(user_id=request.user_id, **function_args)
                        result = await delete_task_tool(input_data)
                        tool_results.append({
                            "tool_call_id": tool_call.id,
                            "result": result
                        })

                # Generate a final response based on tool results
                final_response = await self.generate_final_response(request.user_message, tool_results)

                return AgentResponse(
                    response_text=final_response,
                    tool_calls=[{
                        "name": tc.function.name,
                        "arguments": json.loads(tc.function.arguments),
                        "result": next(tr["result"] for tr in tool_results if tr["tool_call_id"] == tc.id)
                    } for tc in tool_calls],
                    success=True
                )

            else:
                # If no tool calls were made, return the assistant's message directly
                assistant_message = response_message.content or "I processed your request, but no specific task operations were needed."

                return AgentResponse(
                    response_text=assistant_message,
                    tool_calls=[],
                    success=True
                )

        except Exception as e:
            return AgentResponse(
                response_text=f"I encountered an error processing your request: {str(e)}",
                tool_calls=[],
                success=False
            )

    async def generate_final_response(self, user_input: str, tool_results: List[Dict]) -> str:
        """
        Generate a final response based on tool execution results.

        Args:
            user_input: Original user input
            tool_results: Results from executed tools

        Returns:
            Formatted response string
        """
        # Check if any tool failed
        has_errors = any(not result['result']['success'] for result in tool_results)

        if has_errors:
            # Aggregate error messages
            error_messages = [
                result['result'].get('error', 'Unknown error')
                for result in tool_results
                if not result['result']['success']
            ]
            return f"I encountered some issues with your request: {'; '.join(error_messages)}. Please try again or rephrase your request."

        # Aggregate success messages
        success_messages = []
        for result in tool_results:
            result_data = result['result']
            if result_data['success']:
                if 'message' in result_data:
                    success_messages.append(result_data['message'])

        if success_messages:
            return ' '.join(success_messages)
        else:
            return "I processed your request successfully."