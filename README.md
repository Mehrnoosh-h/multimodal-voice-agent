

\# Multimodal Voice AI Customer Support Agent



An agentic AI customer support system built with Python, Ollama, Qwen3, and SQLite.



The project is being developed incrementally to demonstrate AI agents, LLM tool calling, multi-step workflows, human-in-the-loop approval, voice AI, multimodal document understanding, and production-oriented AI engineering.



> \*\*Project status:\*\* In active development. The text-based AI agent and core database tools are implemented. Voice and multimodal capabilities are planned.



\## Project Overview



The goal is to build an AI customer support agent that can:



\- Understand customer requests in natural language

\- Retrieve information from a structured database

\- Select and execute Python tools

\- Investigate billing and appointment issues

\- Handle multi-turn conversations

\- Request confirmation before sensitive actions

\- Eventually process voice, images, and PDFs



The system uses a local LLM rather than relying on a paid cloud LLM API.



\## Technology Stack



| Component | Technology |

|---|---|

| Programming language | Python 3.11 |

| Large language model | Qwen3:8b |

| Local LLM runtime | Ollama |

| Database | SQLite |

| Synthetic data generation | Faker |

| PDF generation | ReportLab |

| Version control | Git and GitHub |



\*\*Planned technologies:\*\* Speech-to-Text, Text-to-Speech, FastAPI, RAG, MCP, Docker, and observability tools.



\## Current Architecture



```text

Customer (Text)

&#x20;     |

&#x20;     v

Python Conversational Agent

&#x20;     |

&#x20;     v

Qwen3:8b via Ollama

&#x20;     |

&#x20;     v

Tool Selection and Execution

&#x20;     |

&#x20;     v

Python Backend Tools

&#x20;     |

&#x20;     v

SQLite Customer Support Database

&#x20;     |

&#x20;     v

Tool Results -> LLM -> Customer Response

```



\## Synthetic Dataset



The project uses synthetic customer support data for a fictional healthcare service provider, Northstar Health Services.



Seven SQLite tables are generated:



1\. `customers`

2\. `providers`

3\. `appointments`

4\. `available\_slots`

5\. `transactions`

6\. `documents`

7\. `support\_cases`



The dataset includes controlled scenarios such as duplicate charges, appointment cancellations, and support requests.



Thirty synthetic PDF documents are also generated.



Generated database and PDF files are excluded from Git version control.



\## Implemented Backend Tools



The following Python functions are implemented in `src/tools.py`:



| Function | Purpose |

|---|---|

| `get\_customer()` | Retrieve customer information |

| `get\_appointments()` | Retrieve appointments |

| `search\_available\_slots()` | Find available appointment slots |

| `get\_transactions()` | Retrieve transaction history |

| `check\_duplicate\_charge()` | Detect duplicate payments and refund resolution |

| `get\_documents()` | Retrieve document metadata |

| `get\_support\_cases()` | Retrieve support cases |

| `cancel\_appointment()` | Cancel an appointment with confirmation |

| `reschedule\_appointment()` | Reschedule an appointment with confirmation |

| `issue\_refund()` | Process a refund with confirmation |

| `create\_support\_ticket()` | Create a customer support case |



The conversational agent currently exposes eight tools. The remaining action tools will be connected in subsequent development steps.



\*\*Safety note:\*\* Confirmation handling and backend business-rule validation are still being strengthened. The system is a demonstration, not a production-ready financial or healthcare application.



\## Implemented AI Agent



The text-based agent currently supports:



\- Local LLM inference with Qwen3:8b

\- LLM-driven tool selection

\- Python function calling

\- Database-backed responses

\- Multiple tool calls within a request

\- Conversation history across turns

\- Confirmation-based refund requests

\- Duplicate-charge investigation and resolution checks



\### Example Interaction



\*\*Customer:\*\*

"My customer ID is C021. Check whether my duplicate charge has already been resolved."



\*\*Agent behavior:\*\*

1\. Selects `check\_duplicate\_charge`

2\. Queries the SQLite database

3\. Identifies two payments of $125 for the same appointment

4\. Detects one completed refund of $125

5\. Recognizes the issue as resolved

6\. Explains the result without initiating another refund



\## Project Structure



```text

multimodal-voice-agent/

├── .gitignore

├── README.md

├── data/

│   ├── customer\_support.db       # Generated locally

│   └── documents/                # Generated locally

└── src/

&#x20;   ├── agent.py

&#x20;   ├── generate\_data.py

&#x20;   ├── generate\_documents.py

&#x20;   ├── test\_tools.py

&#x20;   └── tools.py

```



\## Local Development



\### Requirements



\- Python 3.11

\- Ollama

\- Qwen3:8b



\### Install Python Dependencies



```bash

pip install faker reportlab ollama

```



\### Download the LLM



```bash

ollama pull qwen3:8b

```



\### Generate Synthetic Data



```bash

python src/generate\_data.py

```



\### Generate Synthetic PDF Documents



```bash

python src/generate\_documents.py

```



\### Run the Conversational Agent



```bash

python src/agent.py

```



The database must be generated before using the agent.



\## Development Roadmap



\- \[x] Define project architecture and use cases

\- \[x] Set up Python development environment

\- \[x] Generate synthetic SQLite dataset

\- \[x] Generate synthetic PDF documents

\- \[x] Implement database backend tools

\- \[x] Integrate Ollama and Qwen3:8b

\- \[x] Implement LLM tool calling

\- \[x] Implement conversational text agent

\- \[x] Test duplicate-charge investigation

\- \[ ] Connect appointment cancellation and rescheduling to the agent

\- \[ ] Connect support-ticket creation to the agent

\- \[ ] Strengthen human-in-the-loop approval and backend safeguards

\- \[ ] Implement and test multi-step workflows

\- \[ ] Add robust error handling

\- \[ ] Integrate Speech-to-Text

\- \[ ] Integrate Text-to-Speech

\- \[ ] Build an end-to-end voice agent

\- \[ ] Add image and PDF understanding

\- \[ ] Implement RAG for support policies

\- \[ ] Integrate Model Context Protocol (MCP)

\- \[ ] Build FastAPI endpoints

\- \[ ] Add observability and tracing

\- \[ ] Develop an agent evaluation framework

\- \[ ] Containerize with Docker

\- \[ ] Build a simple user interface

\- \[ ] Prepare a project demo



\## Data and Safety



All customer, appointment, billing, and document data are synthetic.



No real patient or financial records are required.



The project is intended for learning, experimentation, and AI engineering portfolio demonstration.



\## Development Status



\*\*Current milestone:\*\* Text-based agent with database tools and refund-resolution handling.



\*\*Next milestone:\*\* Connect remaining action tools and strengthen human-in-the-loop safety.



This README will be updated as new capabilities are implemented.



