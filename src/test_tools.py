from tools import (
    get_customer,
    get_appointments,
    search_available_slots,
    get_transactions,
    check_duplicate_charge,
    get_documents,
    get_support_cases,
    cancel_appointment,
    reschedule_appointment,
    issue_refund,
    create_support_ticket,
)


CUSTOMER_ID = "C021"


print("\n========================================")
print("1. GET CUSTOMER")
print("========================================")
print(get_customer(CUSTOMER_ID))


print("\n========================================")
print("2. GET APPOINTMENTS")
print("========================================")

appointments_result = get_appointments(CUSTOMER_ID)

print(appointments_result)


print("\n========================================")
print("3. GET TRANSACTIONS")
print("========================================")

print(get_transactions(CUSTOMER_ID))


print("\n========================================")
print("4. CHECK DUPLICATE CHARGE")
print("========================================")

print(check_duplicate_charge(CUSTOMER_ID))


print("\n========================================")
print("5. GET DOCUMENTS")
print("========================================")

print(get_documents(CUSTOMER_ID))


print("\n========================================")
print("6. GET SUPPORT CASES")
print("========================================")

print(get_support_cases(CUSTOMER_ID))


print("\n========================================")
print("7. TEST CANCELLATION SAFETY")
print("========================================")

# confirmed=False means the tool MUST NOT
# modify the database.
# This tests the human-approval safety mechanism.

if appointments_result["appointments"]:

    test_appointment_id = appointments_result[
        "appointments"
    ][0]["appointment_id"]

    cancellation_result = cancel_appointment(
        customer_id=CUSTOMER_ID,
        appointment_id=test_appointment_id,
        confirmed=False
    )

    print(cancellation_result)

else:
    print(
        "No appointment available "
        "for cancellation test."
    )


print("\n========================================")
print("8. SEARCH AVAILABLE SLOTS")
print("========================================")

slots_result = search_available_slots()

print(slots_result)


print("\n========================================")
print("9. TEST RESCHEDULE SAFETY")
print("========================================")

# confirmed=False means the tool MUST NOT
# modify the database.

if (
    appointments_result["appointments"]
    and slots_result["slots"]
):

    test_appointment_id = appointments_result[
        "appointments"
    ][0]["appointment_id"]

    test_slot_id = slots_result[
        "slots"
    ][0]["slot_id"]

    reschedule_result = reschedule_appointment(
        customer_id=CUSTOMER_ID,
        appointment_id=test_appointment_id,
        slot_id=test_slot_id,
        confirmed=False
    )

    print(reschedule_result)

else:
    print(
        "No appointment or available slot "
        "for reschedule test."
    )


print("\n========================================")
print("10. TEST REFUND SAFETY")
print("========================================")

# We already performed the real refund for T100.
# Here we only verify that the tool requires
# confirmation before attempting another refund.

refund_safety_result = issue_refund(
    customer_id=CUSTOMER_ID,
    transaction_id="T099",
    confirmed=False
)

print(refund_safety_result)


print("\n========================================")
print("11. TEST CREATE SUPPORT TICKET")
print("========================================")

ticket_result = create_support_ticket(
    customer_id=CUSTOMER_ID,
    case_type="billing",
    description=(
        "Customer reported a duplicate $125 charge "
        "and requested additional billing review."
    ),
    priority="high"
)

print(ticket_result)


print("\n========================================")
print("12. VERIFY SUPPORT TICKET")
print("========================================")

print(get_support_cases(CUSTOMER_ID))


print("\n========================================")
print("TEST COMPLETE")
print("========================================")