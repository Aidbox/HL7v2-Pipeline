# ADT Update patient information
# This trigger event is used when any patient information has changed but when no other trigger event has occurred.
# For example, an A08 event can be used to notify the receiving systems of a change of address or a name change.
# We recommend that the A08 transaction be used to update fields that are not related to any of the other trigger events.
# The A08 event can include information specific to an episode of care,
# but it can also be used for demographic information only.


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

    if "next_of_kins" in message:
        for item in message["next_of_kins"]:
            entry.append(
                {
                    "resource": prepare_related_persons(item, patient),
                    "request": {"method": "PUT", "url": "RelatedPerson"},
                }
            )

    if "procedures" in message:
        for item in message["procedures"]:
            entry.append(
                {
                    "resource": prepare_procedure(item, patient),
                    "request": {"method": "PUT", "url": "Procedure"},
                }
            )

    if "observations" in message:
        for item in message["observations"]:
            entry.append(
                {
                    "resource": prepare_observation(item, patient, parent=None).dumps(
                        exclude_unset=True
                    ),
                    "request": {"method": "PUT", "url": "Observation"},
                }
            )

    if "diagnosis" in message:
        for item in message["diagnosis"]:
            entry.append(
                {
                    "resource": prepare_condition(item, patient),
                    "request": {"method": "PUT", "url": "Condition"},
                }
            )

    if "allergies" in message:
        for item in message["allergies"]:
            entry.append(
                {
                    "resource": prepare_allergies(item),
                    "request": {"method": "PUT", "url": "AllergyIntolerance"},
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

    if "insurances" in message:
        for item in message["insurances"]:
            data = prepare_coverage(item, patient)

            entry.append(
                {
                    "resource": data[0].dumps(exclude_unset=True),
                    "request": {"method": "PUT", "url": "Organization"},
                }
            )

            entry.append(
                {
                    "resource": data[1].dumps(exclude_unset=True),
                    "request": {"method": "PUT", "url": "Coverage"},
                }
            )

    try:
        API.bundle(entry=entry, type="transaction")
    except requests.exceptions.RequestException as e:
        if e.response is not None:
            print(e.response.json())
