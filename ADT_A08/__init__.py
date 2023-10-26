import requests
import json

from aidbox.base import API

from ADT_A08.observation import prepare_observation
from ADT_A08.patient import prepare_patient
from ADT_A08.allergyintolerance import prepare_allergies
from ADT_A08.encounter import prepare_encounters
from ADT_A08.coverage import prepare_coverage


def run(message):
    entry = []
    patient = prepare_patient(message["patient"])

    if "patient" in message:
        entry.append(
            {
                "resource": patient.model_dump(exclude_unset=True),
                "request": {"method": "POST", "url": "Patient"},
            }
        )

    if "observations" in message:
        for item in message["observations"]:
            entry.append(
                {
                    "resource": prepare_observation(item),
                    "request": {"method": "POST", "url": "Observation"},
                }
            )

    if "allergies" in message:
        for item in message["allergies"]:
            entry.append(
                {
                    "resource": prepare_allergies(item),
                    "request": {"method": "POST", "url": "AllergyIntolerance"},
                }
            )

    if "visit" in message:
        data = prepare_encounters(message["visit"], patient=patient)

        for item in data[0]:
            entry.append(
                {
                    "resource": item.dump(exclude_unset=True),
                    "request": {"method": "PUT", "url": "Location"},
                }
            )

        for item in data[1]:
            entry.append(
                {
                    "resource": item.dump(exclude_unset=True),
                    "request": {"method": "PUT", "url": "Practitioner"},
                }
            )

        entry.append(
            {
                "resource": data[2].dump(exclude_unset=True),
                "request": {"method": "POST", "url": "Encounter"},
            }
        )

    if "insurances" in message:
        for item in message["insurances"]:
            data = prepare_coverage(item, patient)

            entry.append(
                {
                    "resource": data[0].dump(exclude_unset=True),
                    "request": {"method": "PUT", "url": "Organization"},
                }
            )

            entry.append(
                {
                    "resource": data[1].dump(exclude_unset=True),
                    "request": {"method": "POST", "url": "Coverage"},
                }
            )

    try:
        API.bundle(entry=entry, type="transaction")
        print("done!")
    except requests.exceptions.RequestException as e:
        if e.response is not None:
            print(e.response.json())
