
from app.database.chat_repository import (
    create_conversation,
    save_message,
    get_conversation_messages,
    get_all_conversations
)

# TEST 1: Create conversation
conversation_id = create_conversation(
    "Customer Support Test"
)

print("\nTEST 1 - Conversation Created")
print("Conversation ID:", conversation_id)


# TEST 2: Save customer message
save_message(
    conversation_id,
    "user",
    "Where is my order ORD1001?"
)

print("\nTEST 2 - Customer Message Saved")


# TEST 3: Save AI response
save_message(
    conversation_id,
    "assistant",
    "Your order ORD1001 has been shipped."
)

print("\nTEST 3 - AI Response Saved")


# TEST 4: Retrieve conversation history
messages = get_conversation_messages(
    conversation_id
)

print("\nTEST 4 - Conversation History")

for message in messages:
    print(message)


# TEST 5: Retrieve all conversations
conversations = get_all_conversations()

print("\nTEST 5 - All Conversations")

for conversation in conversations:
    print(conversation.id, conversation.title)
