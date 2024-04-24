import requests

from aidbox.base import API

from HL7v2.resources.patient import prepare_patient
from HL7v2.resources.encounter import prepare_encounters
from HL7v2.resources.immunization import prepare_immunization


def run(message):
    entry = []
    patient_group = message.get("patient_group", {})
    patient = prepare_patient(patient_group["patient"])

    if "patient" in patient_group:
        entry.append(
            {
                "resource": patient.dumps(exclude_none=True, exclude_unset=True),
                "request": {"method": "PUT", "url": "Patient"},
            }
        )

    if "visit" in patient_group:
        visit = prepare_encounters(patient_group["visit"], patient=patient)

        for item in visit[0]:
            entry.append(
                {
                    "resource": item.dumps(exclude_unset=True),
                    "request": {"method": "PUT", "url": "Location"},
                }
            )

        for item in visit[1]:
            entry.append(
                {
                    "resource": item.dumps(exclude_unset=True),
                    "request": {"method": "PUT", "url": "Practitioner"},
                }
            )

        entry.append(
            {
                "resource": visit[2].dumps(exclude_unset=True),
                "request": {"method": "PUT", "url": "Encounter"},
            }
        )


    if "immunization" in message:
        immunization = prepare_immunization(message["immunization"], patient)

        entry.append(
            {
                "resource": immunization.dumps(exclude_none=True, exclude_unset=True),
                "request": {"method": "PUT", "url": "Immunization"},
            }
        )

    try:
        API.bundle(entry=entry, type="transaction")
    except requests.exceptions.RequestException as e:
        if e.response is not None:
            print(e.response.json())
