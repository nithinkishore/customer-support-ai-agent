import json
import os
import re
from datetime import datetime

import streamlit as st
from openai import OpenAI

from app.agent.auth import login_customer, register_customer
from app.agent.tools import check_order_status
from app.database.chat_repository import (
    create_conversation,
    save_message,
    get_conversation_messages,
    get_all_conversations,
)
from app.database.init_db import initialize_database
# -----------------------------------------
# RAG: KNOWLEDGE BASE INITIALIZATION
# -----------------------------------------


@st.cache_resource
def initialize_rag():
    from app.rag.knowledge_base import (
        collection,
        index_knowledge_base,
        search_knowledge_base,
    )

    # Refresh the policy knowledge base when the app starts.
    index_knowledge_base()

    return search_knowledge_base


# -----------------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------------

st.set_page_config(
    page_title="Customer Support AI Agent",
    page_icon="🤖",
    layout="centered",
)

# Create required database tables once per Streamlit process.
@st.cache_resource
def initialize_database_once():
    initialize_database()


initialize_database_once()


# -----------------------------------------
# 2. AUTHENTICATION UI
# -----------------------------------------

def clear_customer_chat_state():
    """Prevent one login from inheriting another customer's UI state."""
    for key in (
        "conversation_id",
        "messages",
        "conversation_selector",
    ):
        st.session_state.pop(key, None)


def show_authentication():
    st.title("🤖 Customer Support AI Assistant")
    st.caption("Sign in or create an account to access customer support.")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email address", key="login_email")
            password = st.text_input(
                "Password",
                type="password",
                key="login_password"
            )
            login_submitted = st.form_submit_button(
                "Login",
                use_container_width=True
            )

        if login_submitted:
            if not email.strip() or not password:
                st.error("Please enter your email and password.")
            else:
                result = login_customer(email, password)
                if result.get("success"):
                    clear_customer_chat_state()
                    st.session_state.authenticated = True
                    st.session_state.customer_id = result["customer_id"]
                    st.session_state.customer_name = result["full_name"]
                    st.success("Login successful.")
                    st.rerun()
                else:
                    st.error(result.get("message", "Login failed."))

    with register_tab:
        with st.form("register_form"):
            full_name = st.text_input("Full name", key="register_name")
            email = st.text_input("Email address", key="register_email")
            password = st.text_input(
                "Password (minimum 8 characters)",
                type="password",
                key="register_password"
            )
            confirm_password = st.text_input(
                "Confirm password",
                type="password",
                key="register_confirm_password"
            )
            register_submitted = st.form_submit_button(
                "Create account",
                use_container_width=True
            )

        if register_submitted:
            if not full_name.strip() or not email.strip():
                st.error("Please enter your name and email address.")
            elif len(password) < 8:
                st.error("Password must contain at least 8 characters.")
            elif password != confirm_password:
                st.error("The passwords do not match.")
            else:
                try:
                    result = register_customer(
                        full_name=full_name,
                        email=email,
                        password=password
                    )
                    if result.get("success"):
                        st.success(
                            "Account created. Please use the Login tab."
                        )
                    else:
                        st.error(result.get("message", "Registration failed."))
                except Exception as error:
                    st.error(f"Registration failed: {error}")


if not st.session_state.get("authenticated", False):
    show_authentication()
    st.stop()


# -----------------------------------------
# 3. OLLAMA CONNECTION AND MODEL
# -----------------------------------------

@st.cache_resource
def get_ai_client():
    """Create and reuse one Ollama/OpenAI-compatible client per Streamlit process."""
    api_key = os.getenv("OLLAMA_API_KEY")

    if not api_key:
        try:
            api_key = st.secrets["OLLAMA_API_KEY"]
        except Exception:
            api_key = None

    if api_key:
        return (
            OpenAI(
                base_url="https://ollama.com/v1",
                api_key=api_key,
                timeout=60.0,
                max_retries=0,
            ),
            "deepseek-v4.1-flash",
            "Ollama Cloud",
        )

    return (
        OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
            timeout=90.0,
            max_retries=0,
        ),
        "qwen3:4b-instruct",
        "Local Ollama",
    )


client, MODEL, MODEL_PROVIDER = get_ai_client()

# Keep local Ollama responsive:
# - Disable Qwen3 reasoning mode for routine support replies.
# - Keep the model loaded between requests to reduce cold-start latency.
# - Limit generated tokens and context size to reduce CPU work.
LOCAL_INFERENCE_OPTIONS = (
    {
        "extra_body": {
            "think": False,
            "keep_alive": "10m",
            "options": {
                "num_predict": 96,
                "num_ctx": 2048,
                "temperature": 0.2,
            },
        }
    }
    if MODEL_PROVIDER == "Local Ollama"
    else {}
)

customer_id = st.session_state.customer_id
customer_name = st.session_state.customer_name


# -----------------------------------------
# 4. TOOL DEFINITION
# -----------------------------------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "check_order_status",
            "description": (
                "Retrieve actual order details from the SQLite database. "
                "Use this tool whenever a customer asks about an order."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Customer order ID",
                    }
                },
                "required": ["order_id"],
            },
        },
    }
]


# -----------------------------------------
# 5. SYSTEM PROMPT
# -----------------------------------------

SYSTEM_PROMPT = """
You are a professional e-commerce customer support agent.

Your responsibilities:
1. Help customers with order enquiries and customer support policy questions.
2. Use check_order_status for order-related questions.
3. Never invent order details, delivery dates, or policy details.
4. For policy questions, answer only with information explicitly supported by the retrieved knowledge-base context.
5. If the knowledge-base context does not explicitly answer a policy question, say that the information is unavailable and ask the customer to contact human support.
6. Do not treat missing information as proof that a product, service, warranty, or policy does not exist.
7. Only communicate order details returned by the order-status tool.
8. If an order is not found, inform the customer clearly.
9. Be polite, concise and professional.
"""


# -----------------------------------------
# 6. TOOL DISPATCHER
# -----------------------------------------


def execute_tool(name, arguments, customer_id):
    if name == "check_order_status":
        order_id = arguments.get("order_id")

        if not order_id:
            return {
                "success": False,
                "message": "Order ID is required."
            }

        return check_order_status(
            order_id=order_id,
            customer_id=customer_id
        )

    return {
        "success": False,
        "message": "Unknown tool."
    }



# -----------------------------------------
# 7. CONVERSATION HELPERS
# -----------------------------------------

def load_conversation(conversation_id):
    saved_messages = get_conversation_messages(
        conversation_id,
        customer_id
    )
    st.session_state.conversation_id = conversation_id
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ] + saved_messages


def start_new_conversation():
    timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p")
    new_id = create_conversation(
        title=f"Conversation - {timestamp}",
        customer_id=customer_id
    )
    st.session_state.conversation_id = new_id
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    st.session_state[selector_key] = new_id


# -----------------------------------------
# 8. SESSION INITIALIZATION
# -----------------------------------------

selector_key = f"conversation_selector_{customer_id}"

if "conversation_id" not in st.session_state:
    existing_conversations = get_all_conversations(customer_id)
    if existing_conversations:
        load_conversation(existing_conversations[0].id)
    else:
        start_new_conversation()
elif "messages" not in st.session_state:
    load_conversation(st.session_state.conversation_id)


# -----------------------------------------
# 9. APPLICATION HEADER
# -----------------------------------------

st.title("🤖 Customer Support AI Assistant")
st.caption(f"Powered by {MODEL} | {MODEL_PROVIDER} | Python | SQLite")
st.markdown(
    f"Welcome, **{customer_name}**! Ask me about your order status "
    "or any general customer support question."
)


# -----------------------------------------
# 10. SIDEBAR: CUSTOMER AND CHAT HISTORY
# -----------------------------------------

with st.sidebar:
    st.header("Customer Support")
    st.write(f"Signed in as: **{customer_name}**")
    st.write("AI Assistant: Connected")
    st.write(f"Provider: {MODEL_PROVIDER}")
    st.write(f"Model: {MODEL}")
    st.write("Database: SQLite")

    if st.button("Logout", use_container_width=True):
        clear_customer_chat_state()
        for key in ("authenticated", "customer_id", "customer_name"):
            st.session_state.pop(key, None)
        st.rerun()

    st.divider()
    st.subheader("Chat History")

    if st.button("＋ New Conversation", use_container_width=True):
        start_new_conversation()
        st.rerun()

    conversations = get_all_conversations(customer_id)

    if conversations:
        conversation_ids = [conversation.id for conversation in conversations]
        conversation_titles = {
            conversation.id: (
                conversation.title or f"Conversation {conversation.id}"
            )
            for conversation in conversations
        }

        current_id = st.session_state.conversation_id

        if current_id not in conversation_ids:
            conversation_ids.insert(0, current_id)
            conversation_titles[current_id] = f"Conversation {current_id}"

        if (
            selector_key not in st.session_state
            or st.session_state[selector_key] not in conversation_ids
        ):
            st.session_state[selector_key] = current_id

        selected_id = st.selectbox(
            "Your previous conversations",
            options=conversation_ids,
            format_func=lambda item: (
                f"{conversation_titles.get(item, f'Conversation {item}')} "
                f"(#{item})"
            ),
            key=selector_key,
        )

        if selected_id != st.session_state.conversation_id:
            load_conversation(selected_id)
            st.rerun()

    st.caption(f"Active conversation ID: {st.session_state.conversation_id}")


# -----------------------------------------
# 11. DISPLAY ACTIVE CHAT HISTORY
# -----------------------------------------

for message in st.session_state.messages:
    if message.get("role") not in ("user", "assistant"):
        continue
    with st.chat_message(message["role"]):
        st.markdown(message.get("content") or "")


# -----------------------------------------
# 12. CUSTOMER INPUT
# -----------------------------------------

user_input = st.chat_input("Ask about your order...")

if user_input:
    conversation_id = st.session_state.conversation_id
    # Retrieve policy context only for policy questions.
    # Order lookups use the database tool and do not need vector search.
    rag_context = ""
    contains_order_id = bool(
        re.search(r"\bORD[0-9A-Z-]+\b", user_input, re.IGNORECASE)
    )

    if not contains_order_id:
        try:
            search_knowledge_base = initialize_rag()
            retrieved_chunks = search_knowledge_base(user_input, top_k=3)

            if retrieved_chunks:
                rag_context = "\n\n".join(retrieved_chunks)

        except Exception:
            st.warning(
                "Policy knowledge search is temporarily unavailable."
            )

    # Deterministic guard: do not let the model guess about warranties.
    # If the customer asks about a warranty and the retrieved policy text
    # contains no warranty information, route the question to human support.
    warranty_terms = ("warranty", "guarantee", "guaranteed")
    asks_about_warranty = any(
        term in user_input.lower() for term in warranty_terms
    )
    warranty_is_documented = any(
        term in rag_context.lower() for term in warranty_terms
    )

    if asks_about_warranty and not warranty_is_documented:
        answer = (
            "The available knowledge base does not specify the warranty policy. "
            "Please contact our human support team for confirmation."
        )

        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )
        save_message(
            conversation_id,
            "user",
            user_input,
            customer_id
        )

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            st.markdown(answer)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )
        save_message(
            conversation_id,
            "assistant",
            answer,
            customer_id
        )
        st.stop()
    user_message = {"role": "user", "content": user_input}
    st.session_state.messages.append(user_message)
    save_message(
        conversation_id,
        "user",
        user_input,
        customer_id
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # -------------------------------------
    # 13. PROCESS CUSTOMER REQUEST
    # -------------------------------------

    with st.chat_message("assistant"):
        with st.spinner("AI is processing your request..."):
            try:
                # Keep the system instructions and recent chat turns only.
                # Long histories increase CPU inference time and can crowd the context.
                conversation_history = st.session_state.messages
                # Send only the system prompt and the latest three chat turns.
                # This limits prompt processing while retaining short-term context.
                messages_for_ai = (
                    conversation_history[:1] + conversation_history[-6:]
                    if len(conversation_history) > 7
                    else conversation_history.copy()
                )

                if rag_context:
                    messages_for_ai.insert(
                        1,
                        {
                            "role": "system",
                            "content": (
                                "Relevant customer support policy information:\n\n"
                                f"{rag_context}\n\n"
                                "Use this information as the source of truth for "
                                "policy-related questions. Do not invent, assume, or "
                                "infer policy details. Missing information does not "
                                "mean that a policy, product, service, or warranty does "
                                "not exist. If the retrieved information does not "
                                "explicitly answer the question, say that the information "
                                "is unavailable and ask the customer to contact human "
                                "support. For order-status questions, always use the "
                                "check_order_status tool."
                            ),
                        },
                    )

                request_options = {
                    "model": MODEL,
                    "messages": messages_for_ai,
                    **LOCAL_INFERENCE_OPTIONS,
                }

                # Policy questions do not need function definitions. Supplying
                # tools only for explicit order IDs reduces unnecessary tool
                # selection overhead on ordinary knowledge-base questions.
                if contains_order_id:
                    request_options["tools"] = tools

                response = client.chat.completions.create(**request_options)

                response_message = response.choices[0].message
                tool_calls = response_message.tool_calls or []

                # Store an assistant message here only when the model requested tools.
                # For a normal text response, the answer is appended once below.
                if tool_calls:
                    assistant_tool_message = {
                        "role": "assistant",
                        "content": response_message.content,
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": tool_call.function.name,
                                    "arguments": tool_call.function.arguments,
                                },
                            }
                            for tool_call in tool_calls
                        ],
                    }
                    st.session_state.messages.append(assistant_tool_message)
                    messages_for_ai.append(assistant_tool_message)
                # ---------------------------------
                # 14. EXECUTE REQUESTED TOOLS
                # ---------------------------------

                if tool_calls:
                    for tool_call in tool_calls:
                        tool_name = tool_call.function.name
                        arguments = json.loads(tool_call.function.arguments or "{}")
                        result = execute_tool(
                            tool_name,
                            arguments,
                            customer_id
                        )

                        tool_message = {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result),
                        }
                        st.session_state.messages.append(tool_message)
                        messages_for_ai.append(tool_message)
                    # ---------------------------------
                    # 15. GENERATE FINAL AI RESPONSE
                    # ---------------------------------

                    final_response = client.chat.completions.create(
                        model=MODEL,
                        messages=messages_for_ai,
                        **LOCAL_INFERENCE_OPTIONS,
                    )
                    answer = (
                        final_response.choices[0].message.content
                        or "I could not generate a response."
                    )
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer}
                    )
                else:
                    answer = response_message.content or (
                        "I could not generate a response."
                    )
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer}
                    )

                save_message(
                    conversation_id,
                    "assistant",
                    answer,
                    customer_id
                )
                st.markdown(answer)

            except Exception as error:
                st.error(f"Something went wrong: {error}")
                st.caption(
                    "Your customer message was saved. "
                    "Please check your Ollama connection and API configuration, then try again."
                )
