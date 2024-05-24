import requests

from aidbox.base import (
    API,
    Reference
)

from HL7v2.resources.observation import prepare_observation
from HL7v2.resources.patient import prepare_patient
from HL7v2.resources.allergyintolerance import prepare_allergies
from HL7v2.resources.encounter import prepare_encounters
from HL7v2.resources.coverage import prepare_coverage
from HL7v2.resources.relatedperson import prepare_related_persons
from HL7v2.resources.procedure import prepare_procedure
from HL7v2.resources.condition import prepare_condition
from HL7v2.resources.diagnosticreport import prepare_diagnostic_report

def run(message):
    patient_data = message.get("patient_group")
    observation_data = message.get("observation_requests")
    entry = []
    patient = prepare_patient(patient_data["patient"])

    if "patient" in patient_data:
        entry.append(
            {
                "resource": patient.dumps(exclude_none=True, exclude_unset=True),
                "request": {"method": "PUT", "url": "Patient"},
            }
        )

    if "visit" in patient_data:
        locations, practitioners, encounter = prepare_encounters(patient_data, patient=patient)

        for location in locations:
            entry.append(
                {
                    "resource": location.dumps(exclude_unset=True, exclude_none=True),
                    "request": {"method": "PUT", "url": "Location"},
                }
            )

        for practitioner in practitioners:
            entry.append(
                {
                    "resource": practitioner.dumps(exclude_unset=True, exclude_none=True),
                    "request": {"method": "PUT", "url": "Practitioner"},
                }
            )

        entry.append(
            {
                "resource": encounter.dumps(exclude_unset=True, exclude_none=True),
                "request": {"method": "PUT", "url": "Encounter"},
            }
        )

    for order_group_data in patient_data["order_group"]:
        if "order" in order_group_data:
            main_diagnostic_report, practitioner_roles, observations = prepare_diagnostic_report(order_group_data["order"], patient, encounter=None, parent=None)

            for practitioner_role in practitioner_roles:
                entry.append({
                    "resource": practitioner_role.dumps(exclude_unset=True, exclude_none=True),
                    "request": {"method": "PUT", "url": "PractitionerRole/" + practitioner_role.id}
                })

            for observation in observations:
                entry.append({
                    "resource": observation.dumps(exclude_unset=True, exclude_none=True),
                    "request": {"method": "PUT", "url": "Observation/" + observation.id}
                })

            entry.append({
                "resource": main_diagnostic_report.dumps(exclude_unset=True, exclude_none=True),
                "request": {"method": "PUT", "url": "DiagnosticReport/" + main_diagnostic_report.id}
            })

        for observation_data in order_group_data["observations"]:
            observation, organizations, practitioner_roles = prepare_observation(observation_data, patient, parent = None, specimen=None, encounter=None)

            entry.append({
                "resource": observation.dumps(exclude_unset=True, exclude_none=True),
                "request": {"method": "PUT", "url": "Observation/" + observation.id}
            })

            for organization in organizations:
                entry.append({
                    "resource": organization.dumps(exclude_unset=True, exclude_none=True),
                    "request": {"method": "PUT", "url": "Organization/" + organization.id}
                })

            for practitioner_role in practitioner_roles:
                entry.append({
                    "resource": practitioner_role.dumps(exclude_unset=True, exclude_none=True),
                    "request": {"method": "PUT", "url": "PractitionerRole/" + practitioner_role.id}
                })

        for observation_request_data in order_group_data["observation_requests"]:
            diagnostic_report, practitioner_roles, observations = prepare_diagnostic_report(observation_request_data, patient, encounter=encounter, parent=main_diagnostic_report)

            for practitioner_role in practitioner_roles:
                entry.append({
                    "resource": practitioner_role.dumps(exclude_unset=True, exclude_none=True),
                    "request": {"method": "PUT", "url": "PractitionerRole/" + practitioner_role.id}
                })

            for observation in observations:
                entry.append({
                    "resource": observation.dumps(exclude_unset=True, exclude_none=True),
                    "request": {"method": "PUT", "url": "Observation/" + observation.id}
                })

            for observation_data in observation_request_data.get("observations", []):
                observation, organizations, practitioner_roles = prepare_observation(observation_data, patient, parent = None, specimen=None, encounter=encounter)

                diagnostic_report.result.append(Reference(reference="Observation/" + observation.id))

                entry.append({
                    "resource": observation.dumps(exclude_unset=True, exclude_none=True),
                    "request": {"method": "PUT", "url": "Observation/" + observation.id}
                })

                for organization in organizations:
                    entry.append({
                        "resource": organization.dumps(exclude_unset=True, exclude_none=True),
                        "request": {"method": "PUT", "url": "Organization/" + organization.id}
                    })

                for practitioner_role in practitioner_roles:
                    entry.append({
                        "resource": practitioner_role.dumps(exclude_unset=True, exclude_none=True),
                        "request": {"method": "PUT", "url": "PractitionerRole/" + practitioner_role.id}
                    })

            entry.append({
                "resource": diagnostic_report.dumps(exclude_unset=True, exclude_none=True),
                "request": {"method": "PUT", "url": "DiagnosticReport/" + diagnostic_report.id}
            })

    try:
        API.bundle(entry=entry, type="transaction")
    except requests.exceptions.RequestException as e:
        if e.response is not None:
            print(e.response.json())
