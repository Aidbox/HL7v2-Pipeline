import requests

from aidbox.base import API

from HL7v2.resources.observation import prepare_observation
from HL7v2.resources.patient import prepare_patient
from HL7v2.resources.allergyintolerance import prepare_allergies
from HL7v2.resources.encounter import prepare_encounters
from HL7v2.resources.coverage import prepare_coverage
from HL7v2.resources.relatedperson import prepare_related_persons
from HL7v2.resources.procedure import prepare_procedure
from HL7v2.resources.condition import prepare_condition


def run(message):
    patient_data = message.get("patient_group")
    observation_data = message.get("observation_requests")
    entry = []
    patient = prepare_patient(patient_data["patient"])

    if "patient" in message:
        entry.append(
            {
                "resource": patient.dumps(exclude_none=True, exclude_unset=True),
                "request": {"method": "PUT", "url": "Patient"},
            }
        )

    if "visit" in patient_data:
        data = prepare_encounters(patient_data["visit"], patient=patient)

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

    for item in observation_data:
        observation = prepare_observation(item, patient, parent=None)
        entry.append(
            {
                "resource": observation.dumps(exclude_unset=True),
                "request": {"method": "PUT", "url": "Observation"},
            }
        )

        if item.get("observations"):
            for item in item["observations"]:
                entry.append(
                    {
                        "resource": prepare_observation(
                            item, patient, parent=observation
                        ),
                        "request": {"method": "PUT", "url": "Observation"},
                    }
                )

    try:
        API.bundle(entry=entry, type="transaction")
    except requests.exceptions.RequestException as e:
        if e.response is not None:
            print(e.response.json())
