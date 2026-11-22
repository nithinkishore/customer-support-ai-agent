
import json
from ollama import Client

from app.agent.tools import check_order_status


# 1. Connect to local Ollama
client = Client(
    host="http://localhost:11434"
)

MODEL = "qwen3:4b"


# 2. Define the order lookup tool
tools = [
    {
        "type": "function",
        "function": {
            "name": "check_order_status",
            "description": (
                "Retrieve actual order details from "
                "the SQLite database. Use this tool "
                "whenever a customer asks about an order."
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

        order_id = arguments.get("order_id")

        if not order_id:
            return {
                "success": False,
                "message": "Order ID is required."
            }

        return check_order_status(order_id)

    return {
        "success": False,
        "message": "Unknown tool."
    }


# 4. System instructions
SYSTEM_PROMPT = """
You are a professional e-commerce customer support agent.

Your responsibilities:
1. Help customers with order enquiries.
2. Use check_order_status for order-related questions.
3. Never invent order details or delivery dates.
4. Only communicate information returned by the tool.
5. If an order is not found, clearly inform the customer.
6. Be polite, concise and professional.
7. Do not claim an order is shipped or delivered unless
   the database confirms that status.
"""


# 5. Interactive chatbot
def start_chat():

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    print("\n" + "=" * 50)
    print("       CUSTOMER SUPPORT AI ASSISTANT")
    print("=" * 50)

    print("\nHello! Welcome to Customer Support.")
    print("Ask me about your order status.")
    print("Type 'exit' to end the conversation.\n")

    while True:

        user_input = input("You: ").strip()

        # Exit condition
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nAI: Thank you for contacting customer support!")
            print("Have a great day!")
            break

        if not user_input:
            print("AI: Please enter your question.\n")
            continue

        # Add customer message to conversation
        messages.append({
            "role": "user",
            "content": user_input
        })

        try:

            # 6. Ask Qwen3 to process the question
            response = client.chat(
                model=MODEL,
                messages=messages,
                tools=tools
            )

            messages.append(response.message)

            # 7. Process tool calls
            tool_calls = response.message.tool_calls or []

            if tool_calls:

                for tool_call in tool_calls:

                    tool_name = tool_call.function.name
                    arguments = tool_call.function.arguments

                    print(
                        f"\n[AI TOOL REQUEST: {tool_name}]"
                    )

                    print(
                        f"[TOOL ARGUMENTS: {arguments}]"
                    )

                    result = execute_tool(
                        tool_name,
                        arguments
                    )

                    print(
                        f"[DATABASE RESULT: {result}]"
                    )

                    # Return tool result to Qwen3
                    messages.append({
                        "role": "tool",
                        "name": tool_name,
                        "content": json.dumps(result)
                    })

                # 8. Generate final customer response
                final_response = client.chat(
                    model=MODEL,
                    messages=messages
                )

                messages.append(final_response.message)

                print("\nAI:", final_response.message.content)

            else:

                # Respond normally when no tool is needed
                print("\nAI:", response.message.content)

        except Exception as error:

            print("\nAI: Sorry, I encountered an error.")
            print("Technical details:", error)

        print("\n" + "-" * 50 + "\n")


# 9. Run application
if __name__ == "__main__":
    start_chat()
