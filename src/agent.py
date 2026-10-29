
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
    cancel_appointment,
    reschedule_appointment,
    create_support_ticket,
)


MODEL_NAME = "qwen3:8b"


# ============================================================
# TOOL DEFINITIONS
# ============================================================

def define_tool(name, description, properties, required):
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


def string_parameter(description):
    return {
        "type": "string",
        "description": description,
    }


def confirmation_parameter():
    return {
        "type": "boolean",
        "description": (
            "True only after the customer explicitly confirms "
            "the specific action in the conversation."
        ),
    }


TOOLS = [
    define_tool(
        "get_customer",
        "Get customer account information.",
        {
            "customer_id": string_parameter("Customer ID, such as C021."),
        },
        ["customer_id"],
    ),

    define_tool(
        "get_appointments",
        "Get appointments belonging to a customer.",
        {
            "customer_id": string_parameter("Customer ID."),
        },
        ["customer_id"],
    ),

    define_tool(
        "search_available_slots",
        "Search available appointment slots. All filters are optional.",
        {
            "provider_id": {
                "type": ["string", "null"],
                "description": "Provider ID, or null.",
            },
            "start_date": {
                "type": ["string", "null"],
                "description": "Start date YYYY-MM-DD, or null.",
            },
            "end_date": {
                "type": ["string", "null"],
                "description": "End date YYYY-MM-DD, or null.",
            },
        },
        [],
    ),

    define_tool(
        "get_transactions",
        "Get billing transactions for a customer.",
        {
            "customer_id": string_parameter("Customer ID."),
        },
        ["customer_id"],
    ),

    define_tool(
        "check_duplicate_charge",
        (
            "Check for duplicate completed charges and determine "
            "whether refunds have resolved them."
        ),
        {
            "customer_id": string_parameter("Customer ID."),
        },
        ["customer_id"],
    ),

    define_tool(
        "get_documents",
        "Get document metadata belonging to a customer.",
        {
            "customer_id": string_parameter("Customer ID."),
        },
        ["customer_id"],
    ),

    define_tool(
        "get_support_cases",
        "Get support cases for a customer.",
        {
            "customer_id": string_parameter("Customer ID."),
        },
        ["customer_id"],
    ),

    define_tool(
        "issue_refund",
        (
            "Issue a refund for a completed payment. "
            "This is a sensitive action requiring explicit confirmation."
        ),
        {
            "customer_id": string_parameter("Customer ID."),
            "transaction_id": string_parameter(
                "Specific transaction ID to refund."
            ),
            "confirmed": confirmation_parameter(),
        },
        ["customer_id", "transaction_id", "confirmed"],
    ),

    define_tool(
        "cancel_appointment",
        (
            "Cancel a customer's appointment. "
            "Requires explicit confirmation of the appointment."
        ),
        {
            "customer_id": string_parameter("Customer ID."),
            "appointment_id": string_parameter(
                "Specific appointment ID to cancel."
            ),
            "confirmed": confirmation_parameter(),
        },
        ["customer_id", "appointment_id", "confirmed"],
    ),

    define_tool(
        "reschedule_appointment",
        (
            "Move an appointment to a specific available slot "
            "for the same provider. Requires explicit confirmation."
        ),
        {
            "customer_id": string_parameter("Customer ID."),
            "appointment_id": string_parameter(
                "Appointment ID to reschedule."
            ),
            "slot_id": string_parameter(
                "New available slot ID selected by the customer."
            ),
            "confirmed": confirmation_parameter(),
        },
        ["customer_id", "appointment_id", "slot_id", "confirmed"],
    ),

    define_tool(
        "create_support_ticket",
        (
            "Create a customer support ticket for an issue "
            "that needs investigation or follow-up."
        ),
        {
            "customer_id": string_parameter("Customer ID."),
            "case_type": string_parameter(
                "Issue category, such as billing or appointment."
            ),
            "description": string_parameter(
                "Clear description of the customer's issue."
            ),
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high", "urgent"],
                "description": "Ticket priority.",
            },
        },
        ["customer_id", "case_type", "description"],
    ),
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

    if tool_name == "cancel_appointment":
        return cancel_appointment(
            customer_id=arguments["customer_id"],
            appointment_id=arguments["appointment_id"],
            confirmed=arguments["confirmed"],
        )

    if tool_name == "reschedule_appointment":
        return reschedule_appointment(
            customer_id=arguments["customer_id"],
            appointment_id=arguments["appointment_id"],
            slot_id=arguments["slot_id"],
            confirmed=arguments["confirmed"],
        )

    if tool_name == "create_support_ticket":
        return create_support_ticket(
            customer_id=arguments["customer_id"],
            case_type=arguments["case_type"],
            description=arguments["description"],
            priority=arguments.get("priority", "medium"),
        )

    return {
        "success": False,
        "message": f"Unknown tool: {tool_name}",
    }


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an AI customer support agent for Northstar Health Services.

Use tools whenever customer data is required.
Never invent customer information.
You may use multiple tools to complete a request.

Your available tasks include:
- Customer account lookup
- Appointment lookup
- Available appointment slot search
- Billing transaction lookup
- Duplicate-charge investigation
- Document metadata lookup
- Support case lookup
- Refund requests
- Appointment cancellation
- Appointment rescheduling
- Support ticket creation

SENSITIVE ACTIONS

Refunds, appointment cancellations, and appointment
rescheduling are sensitive actions.

Before performing any sensitive action:
1. Investigate the customer's request using read-only tools.
2. Identify the specific transaction or appointment.
3. Explain exactly what action will be performed.
4. Ask the customer for explicit confirmation.
5. Wait for the customer's confirmation.
6. Only after confirmation, call the action tool
   with confirmed=true.

Do not interpret the initial request to perform an
action as confirmation.

If confirmation has not been received, do not execute
the action.

A confirmation must refer to the specific pending action.
Do not reuse confirmation from an unrelated request.

REFUND RULES

When duplicate charges are detected, normally only
one of the duplicate payments should be refunded.

Check the resolution_status returned by
check_duplicate_charge.

If resolution_status is "resolved", explain that the
duplicate-charge issue has already been resolved.

Do not issue another duplicate-charge refund when
the duplicate-charge issue is resolved.

If resolution_status is "over_refunded", explain
the discrepancy and recommend human investigation.

Do not offer to refund the remaining legitimate
payment without a separate valid reason.

APPOINTMENT RULES

Before cancellation, retrieve the customer's
appointments and identify the correct appointment.

Before rescheduling:
- Retrieve the customer's appointment.
- Search available slots.
- Ensure the proposed slot belongs to the same provider.
- Explain the proposed date and time.
- Request explicit confirmation.

Do not invent appointment availability.

SUPPORT TICKETS

Create support tickets when the customer requests
a ticket or when the customer agrees to escalation.

Do not create unnecessary duplicate support tickets.

Explain the ticket ID after successful creation.

CONVERSATION

Use previous conversation messages and tool results
to understand follow-up responses.

For example, "yes" may confirm a pending action,
but only when the action and its details were clearly
explained immediately beforehand.

If information is missing, ask a clarifying question.

Always report tool errors accurately.
Never claim an action succeeded unless the tool
confirms success.
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
            return assistant_message.get("content", "")

        for tool_call in tool_calls:

            tool_name = tool_call["function"]["name"]
            arguments = tool_call["function"]["arguments"]

            if isinstance(arguments, str):
                arguments = json.loads(arguments)

            print(f"\n[TOOL] {tool_name}")
            print("[ARGUMENTS]", arguments)

            try:
                tool_result = execute_tool(
                    tool_name,
                    arguments,
                )

            except Exception as error:
                tool_result = {
                    "success": False,
                    "message": (
                        f"Tool execution failed: "
                        f"{type(error).__name__}"
                    ),
                }

            print("[RESULT]", tool_result)

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

        if user_message.lower() in {"exit", "quit"}:
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

