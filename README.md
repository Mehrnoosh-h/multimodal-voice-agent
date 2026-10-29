# Multimodal Voice AI Customer Support Agent



**An evolving agentic AI engineering portfolio project** built with Python, Qwen3, Ollama, and SQLite.



> **Status: In development.** A working text-based agent can use database-backed tools, investigate duplicate charges, and handle conversational refund confirmation. Voice, multimodal input, and deployment features are planned.



## Overview



This project explores how to build an AI customer support assistant that goes beyond answering questions. The agent interprets natural-language requests, selects tools, retrieves structured information, and can carry out approved actions.



The demonstration uses **Northstar Health Services**, a fictional healthcare service provider, and entirely synthetic customer data.



### Current capabilities



\- Local LLM inference using **Qwen3:8b** through **Ollama**

\- Multi-turn text conversation with message history

\- LLM-directed Python tool calls and multi-step tool execution

\- SQLite-backed customer, appointment, transaction, and support-case lookups

\- Duplicate-charge detection with refund-resolution status

\- Refund tool with explicit confirmation handling

\- Synthetic dataset and PDF generation scripts



**Important:** This is a learning and portfolio system, not a production-ready healthcare or payments application. Backend authorization, transaction safeguards, and action validation still need strengthening.



## Technology stack



| Area | Technology | Status |

| --- | --- | --- |

| Language | Python 3.11 | Implemented |

| LLM | Qwen3:8b | Implemented |

| Local inference | Ollama | Implemented |

| Database | SQLite | Implemented |

| Synthetic data | Faker | Implemented |

| PDF generation | ReportLab | Implemented |

| Source control | Git and GitHub | Implemented |

| Speech-to-Text / Text-to-Speech | To be selected | Planned |

| API | FastAPI | Planned |

| Retrieval | RAG for support policies | Planned |

| Tool interoperability | Model Context Protocol (MCP) | Planned |

| Containerization | Docker | Planned |

| Observability and evaluation | To be selected | Planned |



## Current architecture



```text

Customer (text input)

        |

        v

Conversational agent (src/agent.py)

        |

        v

Qwen3:8b via Ollama

        |

        v

LLM selects a tool and provides arguments

        |

        v

Python tool dispatcher (src/tools.py)

        |

        v

SQLite customer-support database

        |

        v

Tool result returned to the LLM

        |

        v

Natural-language response to the customer

```



The agent may make multiple tool calls during one request. The current conversation loop retains previous messages within a running session.



## Synthetic data



`src/generate_data.py` creates a SQLite database with seven tables:



| Table | Purpose |

| --- | --- |

| `customers` | Customer profiles and account status |

| `providers` | Healthcare provider information |

| `appointments` | Scheduled and historical appointments |

| `available_slots` | Appointment availability |

| `transactions` | Payments, copays, and refunds |

| `documents` | Metadata linking customers to documents |

| `support_cases` | Customer service requests |



The dataset includes deliberately constructed test cases, including a duplicate-payment scenario. `src/generate_documents.py` creates **30 synthetic PDFs** for document-related experiments.



Generated database files and PDFs are excluded from version control. They can be recreated locally using the scripts below.



## Backend tools



Eleven functions are implemented in `src/tools.py`:



| Tool | Function |

| --- | --- |

| `get_customer()` | Look up a customer |

| `get_appointments()` | List a customer's appointments |

| `search_available_slots()` | Find available appointment slots |

| `get_transactions()` | Retrieve payment history |

| `check_duplicate_charge()` | Identify possible duplicate payments and existing refunds |

| `get_documents()` | Retrieve document metadata and file availability |

| `get_support_cases()` | List support cases |

| `cancel_appointment()` | Cancel an appointment, subject to confirmation |

| `reschedule_appointment()` | Change an appointment, subject to confirmation |

| `issue_refund()` | Create a refund transaction, subject to confirmation |

| `create_support_ticket()` | Open a support case |



**Agent integration:** Eight tools are currently exposed to the conversational agent. Appointment cancellation, rescheduling, and support-ticket creation are implemented in the backend but have not yet been connected to the agent.



### Example: duplicate-charge investigation



**Customer:**



> My customer ID is C021. Check whether my duplicate charge has already been resolved.



**Agent workflow:**



1\. Selects `check_duplicate_charge()`.

2\. Queries the synthetic SQLite database.

3\. Finds two completed payments of $125 associated with appointment `A001`.

4\. Finds one completed refund of $125.

5\. Receives `resolution_status: resolved` from the backend.

6\. Explains that the duplicate-charge issue has already been resolved without attempting another refund.



This is a controlled demonstration scenario. Matching payments by appointment and amount is a heuristic, not a universally reliable duplicate-payment rule.



## Repository structure



```text

multimodal-voice-agent/

|-- .gitignore

|-- README.md

|-- data/

|   |-- customer_support.db       # Generated locally; not tracked

|   `-- documents/               # Generated locally; not tracked

`-- src/

    |-- agent.py                 # Conversational agent

    |-- generate_data.py         # Synthetic SQLite data

    |-- generate_documents.py    # Synthetic PDFs

    |-- test_tools.py            # Backend tool tests

    `-- tools.py                 # Database-backed tools

```



## Run locally



### Prerequisites



\- Python 3.11

\- Ollama installed and running

\- Git (optional, for contributing)



From the project root, install the current Python dependencies:



```bash

pip install faker reportlab ollama

```



Download the local model:



```bash

ollama pull qwen3:8b

```



Generate the SQLite database:



```bash

python src/generate_data.py

```



Generate synthetic PDFs:



```bash

python src/generate_documents.py

```



Start the text-based agent:



```bash

python src/agent.py

```



**Note:** The database must be generated before running the agent. The test script may create new support cases, so run it against disposable synthetic data.



## Development roadmap



### Completed



\- \[x] Define the project architecture and use cases

\- \[x] Configure Python and local LLM environment

\- \[x] Generate and validate synthetic relational data

\- \[x] Generate 30 synthetic PDF documents

\- \[x] Implement 11 backend functions

\- \[x] Connect Qwen3:8b to Python through Ollama

\- \[x] Build a conversational tool-calling agent

\- \[x] Test duplicate-charge detection and refund-resolution reporting

\- \[x] Publish the project to GitHub



### Next: finish the text agent



\- \[ ] Connect cancellation, rescheduling, and ticket creation to the agent

\- \[ ] Strengthen backend refund safeguards and action validation

\- \[ ] Test multi-step customer support workflows

\- \[ ] Improve error handling and failure recovery

\- \[ ] Review agent architecture and core concepts before voice integration



### Planned: voice and multimodal AI



\- \[ ] Add Speech-to-Text (STT)

\- \[ ] Add Text-to-Speech (TTS)

\- \[ ] Implement an end-to-end voice conversation flow

\- \[ ] Add image and PDF understanding

\- \[ ] Add retrieval-augmented generation (RAG) for policies



### Planned: production-oriented engineering



\- \[ ] Integrate MCP-compatible tools

\- \[ ] Add FastAPI endpoints

\- \[ ] Implement logging, tracing, and observability

\- \[ ] Build an agent evaluation dataset and tests

\- \[ ] Containerize with Docker

\- \[ ] Build a simple user interface

\- \[ ] Prepare a reproducible demo and interview documentation



## Safety and limitations



\- All customer and transaction records are **synthetic**.

\- The agent currently relies on a customer ID supplied in conversation; real authentication and authorization have not been implemented.

\- Sensitive actions require stronger backend safeguards, even when the agent asks for confirmation.

\- Refund and appointment tools are demonstrations and should not be connected to real payment or scheduling systems without further validation, auditability, and security controls.

\- Voice, multimodal understanding, RAG, MCP, API serving, and deployment are **not yet implemented**.



## Project updates



This repository is developed incrementally. New features will be committed and pushed as milestones are completed, with this README updated to reflect actual implementation status.



