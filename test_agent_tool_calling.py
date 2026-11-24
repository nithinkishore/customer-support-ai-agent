
import json
from ollama import Client

# Import the database-backed business function
from app.agent.tools import check_order_status


# 1. Connect to local AI model
client = Client(
    host="http://localhost:11434"
)


# 2. Define tool schema for Qwen3
tools = [
    {
        "type": "function",
        "function": {
            "name": "check_order_status",
            "description": (
                "Retrieve actual order information "
                "from the SQLite business database. "
                "Use this tool whenever a customer "
                "asks about a specific order."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Customer order ID"
                    }
                },
                "required": ["order_id"]
            }
        }
    }
]


# 3. Python tool dispatcher
def execute_tool(name, arguments):

    if name == "check_order_status":

        return check_order_status(
            arguments["order_id"]
        )

    return {
        "success": False,
        "message": "Unknown tool."
    }


# 4. Agent instructions
messages = [
    {
        "role": "system",
        "content": """
        You are an e-commerce customer support agent.

        When customers ask about an order,
        use the check_order_status tool.

        Never invent order details.

        Only communicate order information
        returned by the tool.

        If the order is not found,
        clearly inform the customer.
        """
    },
    {
        "role": "user",
        "content": "Please check my order ORD1002."
    }
]


# 5. Ask Qwen3 to process the request
response = client.chat(
    model="qwen3:4b",
    messages=messages,
    tools=tools
)


# 6. Process tool calls
messages.append(response.message)

tool_calls = response.message.tool_calls or []

if not tool_calls:

    print("No tool was requested.")
    print(response.message.content)

else:

    for tool_call in tool_calls:

        tool_name = tool_call.function.name
        arguments = tool_call.function.arguments

        print("\nAI REQUESTED TOOL:")
        print(tool_name)

        print("\nTOOL ARGUMENTS:")
        print(arguments)

        # Execute SQLite database lookup
        result = execute_tool(
            tool_name,
            arguments
        )

        print("\nSQLITE DATABASE RESULT:")
        print(result)

        # Return database result to Qwen3
        messages.append({
            "role": "tool",
            "name": tool_name,
            "content": json.dumps(result)
        })


    # 7. Generate final customer response
    final_response = client.chat(
        model="qwen3:4b",
        messages=messages
    )

    print("\nFINAL CUSTOMER RESPONSE:\n")

    print(final_response.message.content)
