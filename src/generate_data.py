from faker import Faker
import sqlite3
import random
from datetime import datetime

fake = Faker()
DB_PATH = "data/customer_support.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print(f"Connected to database: {DB_PATH}")


# ============================================================
# 1. CUSTOMERS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    date_of_birth TEXT,
    plan_type TEXT,
    account_status TEXT,
    created_at TEXT
)
""")

conn.commit()
print("Customers table created.")

plan_types = ["Basic", "Standard", "Premium"]
account_statuses = ["active", "inactive", "suspended"]

for i in range(1, 31):
    customer_id = f"C{i:03d}"

    cursor.execute("""
        INSERT OR IGNORE INTO customers (
            customer_id,
            first_name,
            last_name,
            email,
            phone,
            date_of_birth,
            plan_type,
            account_status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        customer_id,
        fake.first_name(),
        fake.last_name(),
        fake.unique.email(),
        fake.phone_number(),
        fake.date_of_birth(
            minimum_age=18,
            maximum_age=80
        ).isoformat(),
        random.choice(plan_types),
        random.choice(account_statuses),
        fake.date_time_between(
            start_date="-3y",
            end_date="now"
        ).isoformat()
    ))

conn.commit()
print("30 synthetic customers generated.")


# ============================================================
# 2. PROVIDERS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS providers (
    provider_id TEXT PRIMARY KEY,
    provider_name TEXT NOT NULL,
    specialty TEXT NOT NULL,
    location TEXT NOT NULL,
    active INTEGER NOT NULL
)
""")

conn.commit()
print("Providers table created.")

specialties = [
    "Primary Care",
    "Cardiology",
    "Dermatology",
    "Pediatrics",
    "Orthopedics",
    "Neurology",
    "Endocrinology",
    "Gastroenterology"
]

locations = [
    "Santa Clara",
    "San Jose",
    "Sunnyvale"
]

for i in range(1, 9):
    provider_id = f"P{i:03d}"

    cursor.execute("""
        INSERT OR IGNORE INTO providers (
            provider_id,
            provider_name,
            specialty,
            location,
            active
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        provider_id,
        f"Dr. {fake.first_name()} {fake.last_name()}",
        specialties[i - 1],
        random.choice(locations),
        1
    ))

conn.commit()
print("8 synthetic providers generated.")


# Fix previously generated provider name
cursor.execute("""
UPDATE providers
SET provider_name = 'Dr. Rodney Oliver'
WHERE provider_id = 'P006'
""")

conn.commit()


# ============================================================
# 3. APPOINTMENTS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    provider_id TEXT NOT NULL,
    appointment_date TEXT NOT NULL,
    appointment_time TEXT NOT NULL,
    appointment_type TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),
    FOREIGN KEY (provider_id)
        REFERENCES providers(provider_id)
)
""")

conn.commit()
print("Appointments table created.")

appointment_types = [
    "Routine Checkup",
    "Follow-up",
    "Consultation",
    "Annual Exam"
]

appointment_statuses = [
    "scheduled",
    "completed",
    "cancelled"
]

appointment_times = [
    "09:00",
    "10:00",
    "11:00",
    "13:00",
    "14:00",
    "15:00",
    "16:00"
]

for i in range(1, 61):
    appointment_id = f"A{i:03d}"

    appointment_date = fake.date_between(
        start_date="-6m",
        end_date="+3m"
    )

    cursor.execute("""
        INSERT OR IGNORE INTO appointments (
            appointment_id,
            customer_id,
            provider_id,
            appointment_date,
            appointment_time,
            appointment_type,
            status,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        appointment_id,
        f"C{random.randint(1, 30):03d}",
        f"P{random.randint(1, 8):03d}",
        appointment_date.isoformat(),
        random.choice(appointment_times),
        random.choice(appointment_types),
        random.choice(appointment_statuses),
        fake.date_time_between(
            start_date="-1y",
            end_date="now"
        ).isoformat(),
        datetime.now().isoformat()
    ))

conn.commit()
print("60 synthetic appointments generated.")


# ============================================================
# FIX APPOINTMENT STATUS CONSISTENCY
# ============================================================

today = datetime.now().date().isoformat()

cursor.execute("""
UPDATE appointments
SET status = 'completed',
    updated_at = ?
WHERE appointment_date < ?
AND status = 'scheduled'
""", (
    datetime.now().isoformat(),
    today
))

conn.commit()

print("Past scheduled appointments updated to completed.")


# ============================================================
# 4. AVAILABLE SLOTS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS available_slots (
    slot_id TEXT PRIMARY KEY,
    provider_id TEXT NOT NULL,
    slot_date TEXT NOT NULL,
    slot_time TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    available INTEGER NOT NULL,
    FOREIGN KEY (provider_id)
        REFERENCES providers(provider_id)
)
""")

conn.commit()
print("Available slots table created.")

slot_times = [
    "09:00",
    "10:00",
    "11:00",
    "13:00",
    "14:00",
    "15:00",
    "16:00"
]

for i in range(1, 151):
    slot_id = f"S{i:03d}"

    slot_date = fake.date_between(
        start_date="+1d",
        end_date="+60d"
    )

    cursor.execute("""
        INSERT OR IGNORE INTO available_slots (
            slot_id,
            provider_id,
            slot_date,
            slot_time,
            duration_minutes,
            available
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        slot_id,
        f"P{random.randint(1, 8):03d}",
        slot_date.isoformat(),
        random.choice(slot_times),
        random.choice([30, 45, 60]),
        random.choice([0, 1])
    ))

conn.commit()
print("150 synthetic available slots generated.")


# ============================================================
# 5. TRANSACTIONS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    appointment_id TEXT,
    transaction_date TEXT NOT NULL,
    amount REAL NOT NULL,
    transaction_type TEXT NOT NULL,
    description TEXT,
    payment_method TEXT NOT NULL,
    status TEXT NOT NULL,
    reference_id TEXT,
    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),
    FOREIGN KEY (appointment_id)
        REFERENCES appointments(appointment_id)
)
""")

conn.commit()
print("Transactions table created.")

transaction_types = [
    "payment",
    "copay",
    "refund"
]

payment_methods = [
    "Credit Card",
    "Debit Card",
    "Insurance"
]

transaction_statuses = [
    "completed",
    "failed",
    "pending"
]

for i in range(1, 101):

    transaction_id = f"T{i:03d}"
    appointment_id = f"A{random.randint(1, 60):03d}"

    # Find the actual customer who owns this appointment
    cursor.execute("""
        SELECT customer_id
        FROM appointments
        WHERE appointment_id = ?
    """, (appointment_id,))

    customer_id = cursor.fetchone()[0]

    cursor.execute("""
        INSERT OR IGNORE INTO transactions (
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
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        transaction_id,
        customer_id,
        appointment_id,
        fake.date_time_between(
            start_date="-6m",
            end_date="now"
        ).isoformat(),
        round(random.uniform(25, 500), 2),
        random.choice(transaction_types),
        "Healthcare service transaction",
        random.choice(payment_methods),
        random.choice(transaction_statuses),
        f"REF{i:05d}"
    ))

conn.commit()

print("100 synthetic transactions generated.")


# ============================================================
# SYNCHRONIZE EXISTING TRANSACTIONS
# ============================================================

cursor.execute("""
UPDATE transactions
SET customer_id = (
    SELECT a.customer_id
    FROM appointments a
    WHERE a.appointment_id = transactions.appointment_id
)
WHERE appointment_id IS NOT NULL
""")

conn.commit()

print("Transaction customer IDs synchronized with appointments.")


# ============================================================
# CREATE CONTROLLED DUPLICATE-CHARGE SCENARIO
# ============================================================

cursor.execute("""
SELECT customer_id
FROM appointments
WHERE appointment_id = 'A001'
""")

duplicate_customer_id = cursor.fetchone()[0]

cursor.execute("""
UPDATE transactions
SET customer_id = ?,
    appointment_id = 'A001',
    amount = 125.00,
    transaction_type = 'payment',
    description = 'Office visit payment',
    payment_method = 'Credit Card',
    status = 'completed',
    reference_id = 'DUPLICATE_TEST_1'
WHERE transaction_id = 'T099'
""", (duplicate_customer_id,))

cursor.execute("""
UPDATE transactions
SET customer_id = ?,
    appointment_id = 'A001',
    amount = 125.00,
    transaction_type = 'payment',
    description = 'Office visit payment',
    payment_method = 'Credit Card',
    status = 'completed',
    reference_id = 'DUPLICATE_TEST_2'
WHERE transaction_id = 'T100'
""", (duplicate_customer_id,))

conn.commit()

print("Controlled duplicate-charge scenario created.")


# ============================================================
# 6. DOCUMENTS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    transaction_id TEXT,
    appointment_id TEXT,
    document_type TEXT NOT NULL,
    file_path TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),
    FOREIGN KEY (transaction_id)
        REFERENCES transactions(transaction_id),
    FOREIGN KEY (appointment_id)
        REFERENCES appointments(appointment_id)
)
""")

conn.commit()
print("Documents table created.")

document_types = [
    "invoice",
    "receipt",
    "insurance_statement",
    "appointment_summary"
]

for i in range(1, 31):

    document_id = f"D{i:03d}"
    transaction_id = f"T{random.randint(1, 100):03d}"

    # Get customer and appointment from transaction
    cursor.execute("""
        SELECT customer_id, appointment_id
        FROM transactions
        WHERE transaction_id = ?
    """, (transaction_id,))

    transaction_data = cursor.fetchone()

    customer_id = transaction_data[0]
    appointment_id = transaction_data[1]

    document_type = random.choice(document_types)

    cursor.execute("""
        INSERT OR IGNORE INTO documents (
            document_id,
            customer_id,
            transaction_id,
            appointment_id,
            document_type,
            file_path,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        document_id,
        customer_id,
        transaction_id,
        appointment_id,
        document_type,
        f"data/documents/{document_id}_{document_type}.pdf",
        fake.date_time_between(
            start_date="-6m",
            end_date="now"
        ).isoformat()
    ))

conn.commit()

print("30 synthetic document records generated.")


# ============================================================
# SYNCHRONIZE EXISTING DOCUMENTS
# ============================================================

cursor.execute("""
UPDATE documents
SET customer_id = (
    SELECT t.customer_id
    FROM transactions t
    WHERE t.transaction_id = documents.transaction_id
)
WHERE transaction_id IS NOT NULL
""")

cursor.execute("""
UPDATE documents
SET appointment_id = (
    SELECT t.appointment_id
    FROM transactions t
    WHERE t.transaction_id = documents.transaction_id
)
WHERE transaction_id IS NOT NULL
""")

conn.commit()

print("Document relationships synchronized.")


# ============================================================
# 7. SUPPORT CASES
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS support_cases (
    case_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    case_type TEXT NOT NULL,
    description TEXT NOT NULL,
    priority TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    resolved_at TEXT,
    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
)
""")

conn.commit()

print("Support cases table created.")

case_types = [
    "billing_issue",
    "duplicate_charge",
    "appointment_change",
    "cancellation",
    "document_request",
    "general_question"
]

priorities = [
    "low",
    "medium",
    "high"
]

case_statuses = [
    "open",
    "in_progress",
    "resolved"
]

for i in range(1, 16):

    case_id = f"CASE{i:03d}"
    status = random.choice(case_statuses)

    created_at = fake.date_time_between(
        start_date="-3m",
        end_date="now"
    )

    resolved_at = None

    if status == "resolved":
        resolved_at = fake.date_time_between(
            start_date=created_at,
            end_date="now"
        ).isoformat()

    cursor.execute("""
        INSERT OR IGNORE INTO support_cases (
            case_id,
            customer_id,
            case_type,
            description,
            priority,
            status,
            created_at,
            resolved_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        case_id,
        f"C{random.randint(1, 30):03d}",
        random.choice(case_types),
        fake.sentence(),
        random.choice(priorities),
        status,
        created_at.isoformat(),
        resolved_at
    ))

conn.commit()

print("15 synthetic support cases generated.")


# ============================================================
# FINAL DATABASE SUMMARY
# ============================================================

tables = [
    "customers",
    "providers",
    "appointments",
    "available_slots",
    "transactions",
    "documents",
    "support_cases"
]

print("\n--- Final Database Summary ---")

for table in tables:

    cursor.execute(
        f"SELECT COUNT(*) FROM {table}"
    )

    count = cursor.fetchone()[0]

    print(f"{table}: {count}")


# ============================================================
# RELATIONSHIP VALIDATION
# ============================================================

cursor.execute("""
SELECT COUNT(*)
FROM transactions t
JOIN appointments a
    ON t.appointment_id = a.appointment_id
WHERE t.customer_id != a.customer_id
""")

transaction_mismatches = cursor.fetchone()[0]


cursor.execute("""
SELECT COUNT(*)
FROM documents d
JOIN transactions t
    ON d.transaction_id = t.transaction_id
WHERE d.customer_id != t.customer_id
""")

document_transaction_mismatches = cursor.fetchone()[0]


cursor.execute("""
SELECT COUNT(*)
FROM documents d
JOIN appointments a
    ON d.appointment_id = a.appointment_id
WHERE d.customer_id != a.customer_id
""")

document_appointment_mismatches = cursor.fetchone()[0]


print("\n--- Relationship Validation ---")

print(
    f"Transaction/appointment mismatches: "
    f"{transaction_mismatches}"
)

print(
    f"Document/transaction mismatches: "
    f"{document_transaction_mismatches}"
)

print(
    f"Document/appointment mismatches: "
    f"{document_appointment_mismatches}"
)


# ============================================================
# APPOINTMENT DATE/STATUS VALIDATION
# ============================================================

today = datetime.now().date().isoformat()

cursor.execute("""
SELECT COUNT(*)
FROM appointments
WHERE appointment_date < ?
AND status = 'scheduled'
""", (today,))

past_scheduled = cursor.fetchone()[0]


cursor.execute("""
SELECT COUNT(*)
FROM appointments
WHERE appointment_date > ?
AND status = 'completed'
""", (today,))

future_completed = cursor.fetchone()[0]


print("\n--- Appointment Date/Status Validation ---")

print(
    f"Past appointments still scheduled: "
    f"{past_scheduled}"
)

print(
    f"Future appointments marked completed: "
    f"{future_completed}"
)


# ============================================================
# DUPLICATE CHARGE VALIDATION
# ============================================================

cursor.execute("""
SELECT
    customer_id,
    appointment_id,
    amount,
    COUNT(*) AS duplicate_count
FROM transactions
WHERE status = 'completed'
AND transaction_type IN ('payment', 'copay')
GROUP BY
    customer_id,
    appointment_id,
    amount
HAVING COUNT(*) > 1
""")

duplicate_charges = cursor.fetchall()


print("\n--- Duplicate Charge Validation ---")

print(
    f"Duplicate charge groups found: "
    f"{len(duplicate_charges)}"
)

for charge in duplicate_charges:
    print(charge)


# ============================================================
# CLOSE DATABASE
# ============================================================

conn.close()

print("\nDatabase generation and validation complete.")