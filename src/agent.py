import json
import ollama

from tools import (
    get_customer,
    get_appointments,
    search_available_slots,
    get_transactions,
    check_duplicate_charge,
    get_documents,
    get_support_cases,
    issue_refund,
)


MODEL_NAME = "qwen3:8b"


# ============================================================
# TOOL DEFINITIONS
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_customer",
            "description": "Get customer account information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID such as C021.",
                    }
                },
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_appointments",
            "description": "Get appointments belonging to a customer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                    }
                },
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_available_slots",
            "description": "Search available appointment slots.",
            "parameters": {
                "type": "object",
                "properties": {
                    "provider_id": {
                        "type": ["string", "null"],
                    },
                    "start_date": {
                        "type": ["string", "null"],
                    },
                    "end_date": {
                        "type": ["string", "null"],
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_transactions",
            "description": "Get billing transactions for a customer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                    }
                },
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_duplicate_charge",
            "description": (
                "Check whether a customer has duplicate "
                "completed charges."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                    }
                },
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_documents",
            "description": "Get documents belonging to a customer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                    }
                },
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_support_cases",
            "description": "Get support cases for a customer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                    }
                },
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "issue_refund",
            "description": (
                "Issue a refund for a completed payment. "
                "This is a sensitive action. "
                "Set confirmed=true only when the customer "
                "explicitly confirms the specific refund."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                    },
                    "transaction_id": {
                        "type": "string",
                    },
                    "confirmed": {
                        "type": "boolean",
                    },
                },
                "required": [
                    "customer_id",
                    "transaction_id",
                    "confirmed",
                ],
            },
        },
    },
]


# ============================================================
# TOOL EXECUTION
# ============================================================

def execute_tool(tool_name, arguments):

    if tool_name == "get_customer":
        return get_customer(
            customer_id=arguments["customer_id"]
        )

    if tool_name == "get_appointments":
        return get_appointments(
            customer_id=arguments["customer_id"]
        )

    if tool_name == "search_available_slots":
        return search_available_slots(
            provider_id=arguments.get("provider_id"),
            start_date=arguments.get("start_date"),
            end_date=arguments.get("end_date"),
        )

    if tool_name == "get_transactions":
        return get_transactions(
            customer_id=arguments["customer_id"]
        )

    if tool_name == "check_duplicate_charge":
        return check_duplicate_charge(
            customer_id=arguments["customer_id"]
        )

    if tool_name == "get_documents":
        return get_documents(
            customer_id=arguments["customer_id"]
        )

    if tool_name == "get_support_cases":
        return get_support_cases(
            customer_id=arguments["customer_id"]
        )

    if tool_name == "issue_refund":
        return issue_refund(
            customer_id=arguments["customer_id"],
            transaction_id=arguments["transaction_id"],
            confirmed=arguments["confirmed"],
        )

    return {
        "success": False,
        "message": f"Unknown tool: {tool_name}",
    }


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an AI customer support agent for
Northstar Health Services.

Use tools whenever customer data is required.
Never invent customer information.

You may use multiple tools when necessary.

Refunds are sensitive actions.

Before issuing a refund:
1. Investigate the problem.
2. Identify the specific transaction.
3. Tell the customer what will be refunded.
4. Ask for explicit confirmation.
5. Only after the customer explicitly confirms,
   call issue_refund with confirmed=true.

If the customer has not explicitly confirmed the
specific refund, do not execute it.

When duplicate charges are detected, normally only
ONE of the duplicate transactions should be refunded.

Do not refund all transactions in a duplicate group.
One transaction represents the legitimate original
payment and the other represents the duplicate.

After one duplicate transaction has been successfully
refunded, consider the duplicate-charge issue resolved.

Do not offer to refund the remaining legitimate
transaction unless there is a separate valid reason
for doing so.


Use previous conversation messages and tool results
to understand follow-up responses such as:
"yes", "confirm", or "refund T100".
"""


# ============================================================
# AGENT
# ============================================================

def run_agent(messages):

    for step in range(8):

        response = ollama.chat(
            model=MODEL_NAME,
            messages=messages,
            tools=TOOLS,
        )

        assistant_message = response["message"]
        messages.append(assistant_message)

        tool_calls = assistant_message.get("tool_calls")

        if not tool_calls:
            return assistant_message["content"]

        for tool_call in tool_calls:

            tool_name = tool_call["function"]["name"]
            arguments = tool_call["function"]["arguments"]

            print(
                f"\n[TOOL] {tool_name}"
            )

            print(
                "[ARGUMENTS]",
                arguments
            )

            tool_result = execute_tool(
                tool_name,
                arguments
            )

            print(
                "[RESULT]",
                tool_result
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_name": tool_name,
                    "content": json.dumps(tool_result),
                }
            )

    return (
        "I could not complete the request within "
        "the allowed number of tool-calling steps."
    )


# ============================================================
# INTERACTIVE CHAT
# ============================================================

def main():

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    print("\nNorthstar AI Support Agent")
    print("Type 'exit' to stop.\n")

    while True:

        user_message = input("You: ").strip()

        if user_message.lower() in {
            "exit",
            "quit",
        }:
            print("\nAgent: Goodbye!")
            break

        if not user_message:
            continue

        messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        answer = run_agent(messages)

        print("\nAgent:")
        print(answer)
        print()


if __name__ == "__main__":
    main()