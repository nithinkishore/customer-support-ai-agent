# Customer Support AI Agent

An AI-powered, multi-user customer support application built using **Python, Streamlit, Ollama, Qwen3 4B, SQLite and Retrieval-Augmented Generation (RAG)**.

The application combines a locally hosted Large Language Model (LLM), Python business functions, persistent customer data and a policy knowledge base to handle customer enquiries such as order tracking, returns, refunds, delivery and cancellation policies.

The project demonstrates how Generative AI and agentic workflows can be integrated with application logic, database operations and knowledge retrieval to build a practical customer-support solution.

## Project Overview

Customer support teams frequently handle repetitive enquiries involving order status, delivery updates, returns and refunds.

This project provides an AI-powered interface where customers can authenticate, ask questions in natural language, retrieve order information and receive answers grounded in the available customer-support knowledge base.

The application uses Ollama for LLM execution, SQLite for persistent data and ChromaDB for vector-based knowledge retrieval.

## Key Features

### 1. Local LLM Integration
- Integrates Qwen3 4B through Ollama.
- Connects the Python application to the local model.
- Supports natural-language customer interactions.
- Includes an optional Ollama Cloud configuration.

### 2. Customer Authentication and Security
- Customer registration and login.
- Authenticated customer sessions.
- Customer-specific data access.
- Conversation ownership validation.
- Order lookup authorization to prevent cross-customer access.

### 3. Order Management and Tool Calling
- Integrates LLM tool calling with Python business functions.
- Uses a Python dispatcher to execute predefined tools.
- Retrieves order information from the SQLite database.
- Validates order IDs.
- Checks customer-to-order ownership before returning order information.

### 4. Persistent Database Integration
- SQLite database for application data.
- SQLAlchemy-based database models and operations.
- Persistent customer and order records.
- Persistent conversation and message history.

### 5. Retrieval-Augmented Generation (RAG)
- Uses ChromaDB as the vector database.
- Uses Sentence Transformers (`all-MiniLM-L6-v2`) for text embeddings.
- Loads customer-support policies from a Markdown knowledge-base document.
- Splits policy content into searchable chunks.
- Retrieves relevant information based on customer questions.
- Uses document fingerprinting to avoid unnecessary re-indexing when the source document has not changed.
- Caches the embedding model for reuse.

### 6. Policy-Grounded Customer Support
The knowledge base currently covers:

- Order tracking
- Delivery policy
- Return policy
- Refund policy
- Cancellation policy
- Customer support escalation

The assistant is instructed not to invent unsupported policy details. When the knowledge base does not contain the requested information, it directs customers to human support.

### 7. Streamlit Customer Interface
- Interactive customer-support chat interface.
- Login and registration workflow.
- Customer session management.
- Conversation history.
- New conversation functionality.
- Order-related enquiries.
- AI provider and model information in the interface.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| Streamlit | Customer-facing interface |
| Ollama | Local LLM execution |
| Qwen3 4B | Language model |
| Ollama Python SDK | Model integration |
| SQLite | Persistent data storage |
| SQLAlchemy | Database models and operations |
| ChromaDB | Vector database |
| Sentence Transformers | Text embeddings |
| all-MiniLM-L6-v2 | Embedding model |
| RAG | Knowledge retrieval and grounded responses |
| Pydantic | Data validation support |
| Git & GitHub | Version control |
| VS Code | Development environment |

## Application Architecture

The application follows a modular architecture:

1. **Presentation Layer:** Streamlit interface for customer interaction.
2. **Authentication Layer:** Registration, login and session management.
3. **Agent Layer:** LLM interaction, Python tools and business-function execution.
4. **Database Layer:** SQLite persistence, customer records, orders and conversations.
5. **Knowledge Retrieval Layer:** ChromaDB indexing, embeddings and policy retrieval.
6. **LLM Layer:** Ollama and Qwen3 4B for natural-language understanding and response generation.

## AI Agent Workflow

### Order Enquiry Workflow

1. Customer logs in and submits an order enquiry.
2. The application identifies the authenticated customer.
3. Qwen3 4B interprets the request.
4. The LLM requests the appropriate Python tool.
5. Python executes the order lookup function.
6. Customer ownership and order authorization are validated.
7. The tool returns the verified order information.
8. The LLM generates a customer-friendly response.

### Knowledge-Base Question Workflow

1. Customer submits a policy-related question.
2. The question is processed by the RAG retrieval workflow.
3. Sentence Transformers generate the query embedding.
4. ChromaDB retrieves relevant policy information.
5. Retrieved knowledge is provided to the LLM.
6. The LLM generates a response grounded in the available policy.
7. If the knowledge base does not contain the answer, the customer is directed to human support.

## Project Structure

The project is organized into modular application components. The following represents the main structure; individual test and migration files may evolve as development continues.

```text
customer-support-ai-agent/
│
├── app/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── tools.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── chat_repository.py
│   │   ├── connection.py
│   │   ├── init_db.py
│   │   ├── models.py
│   │   └── seed_db.py
│   │
│   └── rag/
│       ├── __init__.py
│       └── knowledge_base.py
│
├── Knowledge_Base/
│   └── support_policies.md
│
├── Assets/
│
├── streamlit_app.py
├── interactive_agent.py
├── requirements.txt
├── .gitignore
├── README.md
│
└── test_*.py
```

Generated local database and vector-index files are excluded from Git using `.gitignore`.

## Installation and Setup

### Prerequisites

- Python 3.11 or compatible version
- Ollama installed
- Git
- Visual Studio Code (recommended)

### Step 1: Clone the Repository

```bash
git clone https://github.com/nithinkishore/customer-support-ai-agent.git

cd customer-support-ai-agent
```

### Step 2: Create a Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv

.venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install Ollama

Download Ollama:

https://ollama.com/download

Pull the Qwen3 4B model:

```bash
ollama pull qwen3:4b
```

Ensure Ollama is running locally before launching the application.

### Step 5: Launch the Application

```bash
streamlit run streamlit_app.py
```

Open the application in your browser:

```text
http://localhost:8501
```

Register a customer account or log in to begin interacting with the assistant.

The database initialization and knowledge-base indexing are handled by the application initialization workflow.

## Knowledge Base Configuration

The current policy document is:

```text
Knowledge_Base/support_policies.md
```

It contains the policies used by the RAG workflow.

To update the customer-support policies:

1. Edit `support_policies.md`.
2. Save the document.
3. Restart or refresh the application as required.
4. The indexing workflow checks the document fingerprint and re-indexes when the source changes.

The assistant should not invent policy details that are absent from the knowledge base.

## Testing and Validation

The application has been tested through customer interactions and individual component tests.

| Test Area | Validation |
|---|---|
| Ollama integration | Local model connectivity and response generation |
| Authentication | Registration and login |
| Order lookup | Valid and invalid order IDs |
| Order security | Customer ownership validation |
| Database | Initialization and persistent records |
| Chat history | Conversation and message persistence |
| RAG | Policy indexing and retrieval |
| Return policy | Correct retrieval of return conditions |
| Refund policy | Correct retrieval of refund timelines |
| Delivery policy | Retrieval of standard delivery information |
| Unsupported policy | Human-support fallback for warranty questions |

## Performance Observations

Response times vary depending on model initialization, hardware resources, query complexity and retrieval operations.

During local testing, the following response times were observed:

- Return-policy question: approximately 6–12 seconds in separate tests.
- Refund-policy question: approximately 5–6 seconds in separate tests.
- Unsupported warranty question: less than 1 second in one test.

These are individual observations, not formal benchmark results or guaranteed response times.

## Current Scope and Limitations

The current application is a working local prototype and is not yet a production-ready customer-support platform.

Implemented:
- Local LLM integration.
- Customer authentication.
- SQLite database persistence.
- Conversation and message history.
- Customer-specific order authorization.
- Python tool calling.
- RAG-based policy retrieval.
- ChromaDB vector indexing.
- Streamlit customer interface.
- Unsupported-policy fallback.

Not yet established as production capabilities:
- Public cloud deployment.
- Production-grade monitoring and observability.
- Formal load and scalability testing.
- Comprehensive security audit.
- Production integrations with external order-management systems.
- Multi-agent orchestration using LangGraph.

## Future Enhancements

1. Introduce specialized agents for order management, returns and refunds.
2. Implement LangGraph-based agent orchestration.
3. Add human-agent handoff and escalation management.
4. Integrate external CRM and order-management systems.
5. Add advanced evaluation for RAG retrieval quality and LLM response accuracy.
6. Introduce application monitoring, logging and analytics.
7. Implement secure cloud deployment.
8. Add an administrative dashboard for customer-support operations.

## Business Value

The project demonstrates how AI agents can support business operations by:

- Automating repetitive customer enquiries.
- Connecting natural-language requests to deterministic business functions.
- Providing policy-grounded customer responses.
- Maintaining customer-specific conversation history.
- Protecting access to customer and order information.
- Reducing manual effort for routine support activities.
- Establishing a modular foundation for enterprise AI customer-service solutions.

## Author

**Nithin Kishore R S**

AI Project Manager | Automotive Embedded Software | Generative AI | Agentic AI | PMP Certified

LinkedIn: https://www.linkedin.com/in/nithinkishorers

GitHub: https://github.com/nithinkishore

Project Repository: https://github.com/nithinkishore/customer-support-ai-agent

---

*This project is being developed as a practical portfolio initiative to demonstrate the application of Generative AI, Retrieval-Augmented Generation and agentic workflows to real-world business processes.*
