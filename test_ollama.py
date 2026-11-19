
from ollama import Client

# Connect to local Ollama
client = Client(
    host="http://localhost:11434"
)

# Send a request to Qwen3
response = client.chat(
    model="qwen3:4b",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a professional "
                "customer support assistant."
            )
        },
        {
            "role": "user",
            "content": (
                "How can you help a customer "
                "track their order?"
            )
        }
    ]
)

print("\nCUSTOMER SUPPORT AI RESPONSE:\n")

print(response.message.content)
