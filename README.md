# Customer Support AI Agent

An AI-powered customer support agent built using **Python, Ollama, and Qwen3 4B**. This project demonstrates how a locally hosted Large Language Model (LLM) can interact with Python business functions through tool calling to handle customer enquiries.

The current prototype supports order-status enquiries using a Python-based tool and sample order data.

## Project Overview

Customer support teams frequently handle repetitive enquiries such as order tracking and delivery updates. This project explores how an AI agent can understand a customer request, identify the appropriate business function, execute it, and return a natural-language response.

The solution uses a locally hosted LLM through Ollama, reducing dependence on external LLM APIs during development.

## Project Objectives

- Build a beginner-friendly AI customer support agent.
- Integrate a locally hosted LLM using Ollama.
- Implement LLM tool calling with Python.
- Connect AI-generated tool requests to deterministic business functions.
- Validate customer order IDs and handle invalid requests.
- Establish a modular foundation for future database integration and advanced agent capabilities.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| Ollama | Local LLM execution |
| Qwen3 4B | Language model |
| Ollama Python SDK | Python-to-Ollama integration |
| SQLAlchemy | Database integration foundation |
| Pydantic | Data validation support |
| Git & GitHub | Version control and project hosting |
| VS Code | Development environment |

## Architecture

The current prototype follows this workflow:

```text
Customer Query
      |
      v
Python AI Agent
      |
      v
Ollama - Qwen3 4B
      |
      v
LLM Tool Calling
      |
      v
Python Tool Dispatcher
      |
      v
Order Status Function
      |
      v
Sample Order Data
      |
      v
Tool Result Returned to LLM
      |
      v
Customer-Friendly Response
```

## Implemented Features

### 1. Local LLM Integration
- Runs Qwen3 4B locally through Ollama.
- Connects Python to Ollama using the Ollama SDK.
- Tests model connectivity and response generation.

### 2. AI Tool Calling
- Enables the LLM to request a predefined Python function.
- Extracts the requested function name and arguments.
- Uses a Python dispatcher to execute the corresponding function.
- Returns tool results for the LLM to formulate a response.

### 3. Order Status Lookup
- Implements an order-status lookup function.
- Uses sample in-memory order data.
- Tests valid and invalid order IDs.
- Returns appropriate results for supported order enquiries.

## Project Structure

```text
customer-support-ai-agent/
│
├── app/
│   ├── agent/
│   │   ├── __init__.py
│   │   └── tools.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── models.py
│   │
│   └── __init__.py
│
├── test_ollama.py
├── test_order_tool.py
├── test_agent_tool_calling.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

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

Windows:

```powershell
python -m venv .venv

.venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install and Run Ollama

Download Ollama:

https://ollama.com/download

Download the Qwen3 4B model:

```bash
ollama pull qwen3:4b
```

Ensure Ollama is running locally before executing the Python scripts.

### Step 5: Execute the Test Scripts

Test Ollama connectivity:

```bash
python test_ollama.py
```

Test the order lookup function:

```bash
python test_order_tool.py
```

Test AI tool calling:

```bash
python test_agent_tool_calling.py
```

## Testing

The current prototype has been tested for:

| Test Scenario | Expected Behaviour |
|---|---|
| Ollama connectivity | Successful local model connection |
| Valid order ID | Returns the matching sample order information |
| Invalid order ID | Handles an unknown order ID |
| AI tool request | Identifies the requested Python function |
| Tool execution | Dispatches the function and returns its result |

## Current Scope and Limitations

This is an evolving prototype and not yet a production-ready customer support platform.

Current implementation:
- Local LLM integration.
- Python-based tool calling.
- Order-status lookup using sample in-memory data.
- Basic validation and test scenarios.

Not yet implemented:
- Persistent database-backed order management.
- Customer authentication and authorization.
- Retrieval-Augmented Generation (RAG).
- Multi-agent orchestration.
- Web-based customer interface.
- Production deployment, monitoring, and security controls.

## Future Enhancements

1. Integrate SQLite or PostgreSQL for persistent order data.
2. Build a customer-facing interface using Streamlit or FastAPI.
3. Add RAG for FAQs, product documentation, and support knowledge bases.
4. Introduce LangGraph for more advanced agent workflows.
5. Add customer authentication and role-based access control.
6. Implement logging, monitoring, and evaluation.
7. Deploy the application as a secure customer support service.

## Business Value

The project demonstrates how AI agents can support business operations by:

- Automating repetitive customer enquiries.
- Connecting natural-language requests to business functions.
- Reducing manual effort for routine support tasks.
- Providing a foundation for scalable AI-enabled customer service workflows.

## Author

**Nithin Kishore R S**

AI Project Manager | Automotive Embedded Software | Generative AI | Agentic AI | PMP Certified

LinkedIn: https://www.linkedin.com/in/nithinkishorers

GitHub: https://github.com/nithinkishore

---

*This project is being developed as a practical learning and portfolio initiative to demonstrate the application of Generative AI and agentic workflows to real-world business processes.*