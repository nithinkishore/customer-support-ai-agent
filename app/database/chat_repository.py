from datetime import datetime

from app.database.connection import SessionLocal
from app.database.models import Conversation, ChatMessage


def create_conversation(title="New Conversation", customer_id=None):
    """Create a conversation owned by one authenticated customer."""
    if customer_id is None:
        raise ValueError("customer_id is required to create a conversation.")

    db = SessionLocal()
    try:
        conversation = Conversation(
            title=title,
            customer_id=customer_id
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation.id
    finally:
        db.close()


def _get_owned_conversation(db, conversation_id, customer_id):
    if customer_id is None:
        raise PermissionError("Authentication required.")
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.customer_id == customer_id
        )
        .first()
    )
    if conversation is None:
        raise PermissionError("Conversation not found for this customer.")
    return conversation


def save_message(conversation_id, role, content, customer_id):
    """Save a message only if the conversation belongs to this customer."""
    if customer_id is None:
        raise PermissionError("Authentication required.")
    db = SessionLocal()
    try:
        conversation = _get_owned_conversation(
            db, conversation_id, customer_id
        )
        message = ChatMessage(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        conversation.updated_at = datetime.utcnow()
        db.add(message)
        db.commit()
        db.refresh(message)
        return message.id
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_conversation_messages(conversation_id, customer_id):
    """Retrieve history only after verifying conversation ownership."""
    if customer_id is None:
       raise PermissionError("Authentication required.")
    db = SessionLocal()
    try:
        _get_owned_conversation(db, conversation_id, customer_id)
        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )
        return [
            {"role": message.role, "content": message.content}
            for message in messages
        ]
    finally:
        db.close()



def get_all_conversations(customer_id):
    """Return only conversations owned by the authenticated customer."""

    if customer_id is None:
        raise PermissionError("Authentication required.")

    db = SessionLocal()

    try:
        return (
            db.query(Conversation)
            .filter(Conversation.customer_id == customer_id)
            .order_by(Conversation.updated_at.desc())
            .all()
        )
    finally:
        db.close()