# ADT Register a patient
# An A04 event signals that the patient has arrived or checked in as a one-time,
# or recurring outpatient, and is not assigned to a bed.
# One example might be its use to signal the beginning of a visit to the Emergency Room (= Casualty, etc.).
# Note that some systems refer to these events as outpatient registrations or emergency admissions.
# PV1-44 - Admit Date/Time is used for the visit start date/time.

import requests

from aidbox.base import API

from HL7v2.resources.patient import prepare_patient
from HL7v2.resources.encounter import prepare_encounters


def run(message):
    message = message.get("patient_group", {})
    entry = []
    patient = prepare_patient(message["patient"])

    if "patient" in message:
        entry.append(
            {
                "resource": patient.dumps(exclude_none=True, exclude_unset=True),
                "request": {"method": "PUT", "url": "Patient"},
            }
        )

    if "visit" in message:
        data = prepare_encounters(message["visit"], patient=patient)

        for item in data[0]:
            entry.append(
                {
                    "resource": item.dumps(exclude_unset=True),
                    "request": {"method": "PUT", "url": "Location"},
                }
            )

        for item in data[1]:
            entry.append(
                {
                    "resource": item.dumps(exclude_unset=True),
                    "request": {"method": "PUT", "url": "Practitioner"},
                }
            )

        entry.append(
            {
                "resource": data[2].dumps(exclude_unset=True),
                "request": {"method": "PUT", "url": "Encounter"},
            }
        )

    try:
        API.bundle(entry=entry, type="transaction")
    except requests.exceptions.RequestException as e:
        if e.response is not None:
            print(e.response.json())
