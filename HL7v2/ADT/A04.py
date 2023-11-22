# ADT Register a patient
# An A04 event signals that the patient has arrived or checked in as a one-time,
# or recurring outpatient, and is not assigned to a bed.
# One example might be its use to signal the beginning of a visit to the Emergency Room (= Casualty, etc.).
# Note that some systems refer to these events as outpatient registrations or emergency admissions.
# PV1-44 - Admit Date/Time is used for the visit start date/time.


def run(message):
    entry = []
