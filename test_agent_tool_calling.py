
import json
from ollama import Client

# 1. Connect to local AI model
client = Client(
    host="http://localhost:11434"
)

# 2. Sample business database
orders = {
    "ORD1001": {
        "customer": "John",
        "product": "Laptop",
        "status": "Shipped"
    },
    "ORD1002": {
        "customer": "Sarah",
        "product": "Mobile",
        "status": "Delivered"
    },
    "ORD1003": {
        "customer": "David",
        "product": "Headphones",
        "status": "Processing"
    }
}


# 3. Business tool
def check_order_status(order_id: str):

    order = orders.get(order_id)

    if order is None:
        return {
            "success": False,
            "message": "Order not found."
        }

    return {
        "success": True,
        "order_id": order_id,
        "customer": order["customer"],
        "product": order["product"],
        "status": order["status"]
    }


# 4. Tool schema provided to Qwen3
tools = [
    {
        "type": "function",
        "function": {
            "name": "check_order_status",
            "description": (
                "Retrieve the actual status of an "
                "order from the business database. "
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


# 5. Python tool dispatcher
def execute_tool(name, arguments):

    if name == "check_order_status":
        return check_order_status(
            arguments["order_id"]
        )

    return {
        "success": False,
        "message": "Unknown tool."
    }


# 6. Agent instructions
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
        "content": (
            "Please check my order ORD1001."
        )
    }
]


# 7. Ask Qwen3 to process the request
response = client.chat(
    model="qwen3:4b",
    messages=messages,
    tools=tools
)

# 8. Process tool calls
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

        # Execute the Python function
        result = execute_tool(
            tool_name,
            arguments
        )

        print("\nACTUAL DATABASE RESULT:")
        print(result)

        # Return result to Qwen3
        messages.append({
            "role": "tool",
            "name": tool_name,
            "content": json.dumps(result)
        })

    # 9. Ask Qwen3 for the final response
    final_response = client.chat(
        model="qwen3:4b",
        messages=messages
    )

    print("\nFINAL CUSTOMER RESPONSE:\n")

    print(final_response.message.content)
