import sqlite3
from pathlib import Path


DB_PATH = "data/customer_support.db"


def get_connection():
    """Create and return a SQLite database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# TOOL 1: GET CUSTOMER
# ============================================================

def get_customer(customer_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM customers
        WHERE customer_id = ?
    """, (customer_id,))

    customer = cursor.fetchone()
    conn.close()

    if customer is None:
        return {
            "success": False,
            "message": "Customer not found."
        }

    return {
        "success": True,
        "customer": dict(customer)
    }


# ============================================================
# TOOL 2: GET CUSTOMER APPOINTMENTS
# ============================================================

def get_appointments(customer_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            a.appointment_id,
            a.appointment_date,
            a.appointment_time,
            a.appointment_type,
            a.status,
            p.provider_id,
            p.provider_name,
            p.specialty,
            p.location
        FROM appointments a
        JOIN providers p
            ON a.provider_id = p.provider_id
        WHERE a.customer_id = ?
        ORDER BY
            a.appointment_date,
            a.appointment_time
    """, (customer_id,))

    appointments = [
        dict(row)
        for row in cursor.fetchall()
    ]

    conn.close()

    return {
        "success": True,
        "customer_id": customer_id,
        "count": len(appointments),
        "appointments": appointments
    }


# ============================================================
# TOOL 3: SEARCH AVAILABLE SLOTS
# ============================================================

def search_available_slots(
    provider_id=None,
    start_date=None,
    end_date=None
):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            s.slot_id,
            s.provider_id,
            p.provider_name,
            p.specialty,
            p.location,
            s.slot_date,
            s.slot_time,
            s.duration_minutes
        FROM available_slots s
        JOIN providers p
            ON s.provider_id = p.provider_id
        WHERE s.available = 1
    """

    parameters = []

    if provider_id:
        query += " AND s.provider_id = ?"
        parameters.append(provider_id)

    if start_date:
        query += " AND s.slot_date >= ?"
        parameters.append(start_date)

    if end_date:
        query += " AND s.slot_date <= ?"
        parameters.append(end_date)

    query += """
        ORDER BY
            s.slot_date,
            s.slot_time
        LIMIT 20
    """

    cursor.execute(query, parameters)

    slots = [
        dict(row)
        for row in cursor.fetchall()
    ]

    conn.close()

    return {
        "success": True,
        "count": len(slots),
        "slots": slots
    }


# ============================================================
# TOOL 4: GET TRANSACTIONS
# ============================================================

def get_transactions(customer_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            transaction_id,
            appointment_id,
            transaction_date,
            amount,
            transaction_type,
            description,
            payment_method,
            status,
            reference_id
        FROM transactions
        WHERE customer_id = ?
        ORDER BY transaction_date DESC
    """, (customer_id,))

    transactions = [
        dict(row)
        for row in cursor.fetchall()
    ]

    conn.close()

    return {
        "success": True,
        "customer_id": customer_id,
        "count": len(transactions),
        "transactions": transactions
    }


# ============================================================
# TOOL 5: CHECK DUPLICATE CHARGE
# ============================================================

def check_duplicate_charge(customer_id):
    """
    Detect duplicate completed payments and determine whether
    the duplicate-charge problem has already been resolved by refunds.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT appointment_id, amount, COUNT(*) AS duplicate_count
        FROM transactions
        WHERE customer_id = ?
          AND status = 'completed'
          AND transaction_type IN ('payment', 'copay')
          AND appointment_id IS NOT NULL
        GROUP BY appointment_id, amount
        HAVING COUNT(*) > 1
    """, (customer_id,))

    duplicate_groups = cursor.fetchall()
    results = []

    for group in duplicate_groups:
        appointment_id = group["appointment_id"]
        amount = group["amount"]
        duplicate_count = group["duplicate_count"]

        cursor.execute("""
            SELECT *
            FROM transactions
            WHERE customer_id = ?
              AND appointment_id = ?
              AND amount = ?
              AND status = 'completed'
              AND transaction_type IN ('payment', 'copay')
            ORDER BY transaction_date
        """, (customer_id, appointment_id, amount))

        payment_rows = cursor.fetchall()
        payments = [dict(row) for row in payment_rows]
        payment_ids = [row["transaction_id"] for row in payment_rows]

        refunds = []
        for payment_id in payment_ids:
            cursor.execute("""
                SELECT *
                FROM transactions
                WHERE customer_id = ?
                  AND transaction_type = 'refund'
                  AND status = 'completed'
                  AND reference_id = ?
            """, (customer_id, f"REFUND_FOR_{payment_id}"))
            refunds.extend(dict(row) for row in cursor.fetchall())

        refund_count = len(refunds)
        expected_refunds = duplicate_count - 1

        if refund_count == 0:
            resolution_status = "unresolved"
        elif refund_count == expected_refunds:
            resolution_status = "resolved"
        elif refund_count > expected_refunds:
            resolution_status = "over_refunded"
        else:
            resolution_status = "partially_resolved"

        results.append({
            "appointment_id": appointment_id,
            "amount": amount,
            "duplicate_count": duplicate_count,
            "expected_refunds": expected_refunds,
            "refund_count": refund_count,
            "resolution_status": resolution_status,
            "transactions": payments,
            "refunds": refunds
        })

    conn.close()

    return {
        "success": True,
        "customer_id": customer_id,
        "duplicate_found": len(results) > 0,
        "duplicate_groups": results
    }


# ============================================================
# TOOL 6: GET CUSTOMER DOCUMENTS
# ============================================================

def get_documents(customer_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            document_id,
            transaction_id,
            appointment_id,
            document_type,
            file_path,
            created_at
        FROM documents
        WHERE customer_id = ?
        ORDER BY created_at DESC
    """, (customer_id,))

    documents = []

    for row in cursor.fetchall():
        document = dict(row)

        document["file_exists"] = Path(
            document["file_path"]
        ).exists()

        documents.append(document)

    conn.close()

    return {
        "success": True,
        "customer_id": customer_id,
        "count": len(documents),
        "documents": documents
    }


# ============================================================
# TOOL 7: GET SUPPORT CASES
# ============================================================

def get_support_cases(customer_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            case_id,
            case_type,
            description,
            priority,
            status,
            created_at,
            resolved_at
        FROM support_cases
        WHERE customer_id = ?
        ORDER BY created_at DESC
    """, (customer_id,))

    cases = [
        dict(row)
        for row in cursor.fetchall()
    ]

    conn.close()

    return {
        "success": True,
        "customer_id": customer_id,
        "count": len(cases),
        "support_cases": cases
    }


# ============================================================
# TOOL 8: CANCEL APPOINTMENT
# ============================================================

def cancel_appointment(
    customer_id,
    appointment_id,
    confirmed=False
):
    if not confirmed:
        return {
            "success": False,
            "requires_confirmation": True,
            "message":
                "Customer confirmation is required "
                "before cancelling an appointment."
        }

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            appointment_id,
            customer_id,
            status
        FROM appointments
        WHERE appointment_id = ?
    """, (appointment_id,))

    appointment = cursor.fetchone()

    if appointment is None:
        conn.close()

        return {
            "success": False,
            "message": "Appointment not found."
        }

    if appointment["customer_id"] != customer_id:
        conn.close()

        return {
            "success": False,
            "message":
                "Appointment does not belong "
                "to this customer."
        }

    if appointment["status"] == "cancelled":
        conn.close()

        return {
            "success": False,
            "message":
                "Appointment is already cancelled."
        }

    cursor.execute("""
        UPDATE appointments
        SET status = 'cancelled',
            updated_at = CURRENT_TIMESTAMP
        WHERE appointment_id = ?
    """, (appointment_id,))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "appointment_id": appointment_id,
        "status": "cancelled"
    }


# ============================================================
# TOOL 9: RESCHEDULE APPOINTMENT
# ============================================================

def reschedule_appointment(
    customer_id,
    appointment_id,
    slot_id,
    confirmed=False
):
    if not confirmed:
        return {
            "success": False,
            "requires_confirmation": True,
            "message":
                "Customer confirmation is required "
                "before rescheduling an appointment."
        }

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM appointments
        WHERE appointment_id = ?
    """, (appointment_id,))

    appointment = cursor.fetchone()

    if appointment is None:
        conn.close()

        return {
            "success": False,
            "message": "Appointment not found."
        }

    if appointment["customer_id"] != customer_id:
        conn.close()

        return {
            "success": False,
            "message":
                "Appointment does not belong "
                "to this customer."
        }

    cursor.execute("""
        SELECT *
        FROM available_slots
        WHERE slot_id = ?
        AND available = 1
    """, (slot_id,))

    slot = cursor.fetchone()

    if slot is None:
        conn.close()

        return {
            "success": False,
            "message":
                "The requested slot is not available."
        }

    if slot["provider_id"] != appointment["provider_id"]:
        conn.close()

        return {
            "success": False,
            "message":
                "The selected slot belongs to "
                "a different provider."
        }

    cursor.execute("""
        UPDATE appointments
        SET appointment_date = ?,
            appointment_time = ?,
            status = 'scheduled',
            updated_at = CURRENT_TIMESTAMP
        WHERE appointment_id = ?
    """, (
        slot["slot_date"],
        slot["slot_time"],
        appointment_id
    ))

    cursor.execute("""
        UPDATE available_slots
        SET available = 0
        WHERE slot_id = ?
    """, (slot_id,))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "appointment_id": appointment_id,
        "new_date": slot["slot_date"],
        "new_time": slot["slot_time"],
        "slot_id": slot_id
    }


# ============================================================
# TOOL 10: ISSUE REFUND
# ============================================================

def issue_refund(
    customer_id,
    transaction_id,
    confirmed=False
):
    """
    Issue a refund for a completed payment or copay.

    This is a sensitive action and requires explicit
    customer confirmation.
    """

    if not confirmed:
        return {
            "success": False,
            "requires_confirmation": True,
            "message":
                "Customer confirmation is required "
                "before issuing a refund."
        }

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM transactions
        WHERE transaction_id = ?
    """, (transaction_id,))

    transaction = cursor.fetchone()

    if transaction is None:
        conn.close()

        return {
            "success": False,
            "message": "Transaction not found."
        }

    if transaction["customer_id"] != customer_id:
        conn.close()

        return {
            "success": False,
            "message":
                "Transaction does not belong "
                "to this customer."
        }

    if transaction["status"] != "completed":
        conn.close()

        return {
            "success": False,
            "message":
                "Only completed transactions "
                "can be refunded."
        }

    if transaction["transaction_type"] not in (
        "payment",
        "copay"
    ):
        conn.close()

        return {
            "success": False,
            "message":
                "This transaction type "
                "cannot be refunded."
        }

    # Prevent duplicate refunds.
    refund_reference = f"REFUND_FOR_{transaction_id}"

    cursor.execute("""
        SELECT transaction_id
        FROM transactions
        WHERE reference_id = ?
    """, (refund_reference,))

    existing_refund = cursor.fetchone()

    if existing_refund is not None:
        conn.close()

        return {
            "success": False,
            "message":
                "A refund has already been issued "
                "for this transaction."
        }

    # Generate the next transaction ID.
    cursor.execute("""
        SELECT MAX(
            CAST(
                SUBSTR(transaction_id, 2)
                AS INTEGER
            )
        )
        FROM transactions
    """)

    max_id = cursor.fetchone()[0] or 0
    new_transaction_id = f"T{max_id + 1:03d}"

    # Create refund transaction.
    cursor.execute("""
        INSERT INTO transactions (
            transaction_id,
            customer_id,
            appointment_id,
            transaction_date,
            amount,
            transaction_type,
            description,
            payment_method,
            status,
            reference_id
        )
        VALUES (
            ?,
            ?,
            ?,
            CURRENT_TIMESTAMP,
            ?,
            'refund',
            ?,
            ?,
            'completed',
            ?
        )
    """, (
        new_transaction_id,
        customer_id,
        transaction["appointment_id"],
        -abs(transaction["amount"]),
        f"Refund for {transaction_id}",
        transaction["payment_method"],
        refund_reference
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "refund_transaction_id": new_transaction_id,
        "original_transaction_id": transaction_id,
        "refund_amount": abs(transaction["amount"]),
        "message": "Refund issued successfully."
    }

# ============================================================
# TOOL 11: CREATE SUPPORT TICKET
# ============================================================

def create_support_ticket(
    customer_id,
    case_type,
    description,
    priority="medium"
):
    """
    Create a new support case when the AI agent cannot
    fully resolve a customer's issue.
    """

    conn = get_connection()
    cursor = conn.cursor()

    # Verify that the customer exists.
    cursor.execute("""
        SELECT customer_id
        FROM customers
        WHERE customer_id = ?
    """, (customer_id,))

    customer = cursor.fetchone()

    if customer is None:
        conn.close()

        return {
            "success": False,
            "message": "Customer not found."
        }

    # Validate priority.
    valid_priorities = {
        "low",
        "medium",
        "high",
        "urgent"
    }

    priority = priority.lower()

    if priority not in valid_priorities:
        conn.close()

        return {
            "success": False,
            "message":
                "Priority must be low, medium, high, or urgent."
        }

    # Generate the next case ID.
    cursor.execute("""
        SELECT MAX(
            CAST(
                SUBSTR(case_id, 5)
                AS INTEGER
            )
        )
        FROM support_cases
    """)

    max_id = cursor.fetchone()[0] or 0
    new_case_id = f"CASE{max_id + 1:03d}"

    # Create the support case.
    cursor.execute("""
        INSERT INTO support_cases (
            case_id,
            customer_id,
            case_type,
            description,
            priority,
            status,
            created_at,
            resolved_at
        )
        VALUES (
            ?,
            ?,
            ?,
            ?,
            ?,
            'open',
            CURRENT_TIMESTAMP,
            NULL
        )
    """, (
        new_case_id,
        customer_id,
        case_type,
        description,
        priority
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "case_id": new_case_id,
        "customer_id": customer_id,
        "case_type": case_type,
        "priority": priority,
        "status": "open",
        "message": "Support ticket created successfully."
    }

# ============================================================
# SIMPLE TESTS
# ============================================================

if __name__ == "__main__":

    print("\n--- Customer Test ---")
    print(get_customer("C021"))

    print("\n--- Appointment Test ---")
    print(get_appointments("C021"))

    print("\n--- Duplicate Charge Test ---")
    print(check_duplicate_charge("C021"))

    print("\n--- Document Test ---")
    print(get_documents("C021"))

    print("\n--- Refund Safety Test ---")
    print(
        issue_refund(
            customer_id="C021",
            transaction_id="T100",
            confirmed=False
        )
    )