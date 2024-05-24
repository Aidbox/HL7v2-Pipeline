# The function of this message is to initiate the transmission of information about an order.
# This includes placing new orders, cancellation of existing orders, discontinuation, holding, etc.
# ORM messages can originate also with a placer, filler, or an interested third party.

import requests

from aidbox.resource.servicerequest import ServiceRequest
from aidbox.base import API, Reference, Identifier, CodeableConcept, Coding

from HL7v2 import get_md5
from HL7v2.resources.observation import prepare_observation
from HL7v2.resources.patient import prepare_patient
from HL7v2.resources.allergyintolerance import prepare_allergies
from HL7v2.resources.encounter import prepare_encounters
from HL7v2.resources.coverage import prepare_coverage
from HL7v2.resources.relatedperson import prepare_related_persons
from HL7v2.resources.procedure import prepare_procedure
from HL7v2.resources.condition import prepare_condition


def run(message):
    patient_group = message.get("patient_group", {})
    order_group = message.get("order_group", [])
    observations = message.get("observations", [])
    entry = []
    patient = prepare_patient(patient_group["patient"])

    if "patient" in patient_group:
        entry.append(
            {
                "resource": patient.dumps(exclude_none=True, exclude_unset=True),
                "request": {"method": "PUT", "url": "Patient"},
            }
        )

    if "visit" in patient_group:
        data = prepare_encounters(patient_group["visit"], patient=patient)

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

    for item in order_group:
        order = item.get("order", {})
        requester = order.get("requester", {})
        identifiers = order.get("identifier", {})
        requisitions = order.get("requisition", [])
        occurrence = order.get("occurrence", {})
        main_request_id = get_md5([])

        main_request = ServiceRequest(
            id=main_request_id,
            status="active",
            subject=Reference(reference="Patient/" + (patient.id or "")),
            intent="order",
        )

        if requisitions[0]:
            main_request.requisition = Identifier(
                value=requisitions[0].get("identifier"),
                system=requisitions[0].get("system", None),
            )

        for identifier in identifiers.keys():
            main_request.identifier.append(
                Identifier(
                    system=identifier,
                    value=identifiers[identifier].get("identifier", None),
                )
            )

        entry.append(
            {
                "resource": main_request.dumps(exclude_unset=True, exclude_none=True),
                "request": {"method": "PUT", "url": "ServiceRequest"},
            }
        )

        for observation_request in item.get("observation_requests", []):
            code = observation_request.get("code", {})
            identifier = observation_request.get("identifier", {})
            requester = observation_request.get("requester", {})
            id: str = get_md5([])
            request = ServiceRequest(
                id=id,
                status="",
                subject=Reference(),
                basedOn=[Reference(reference="ServiceRequest/" + main_request_id)],
                intent="",
            )

            if "code" in code:
                request.code = CodeableConcept(
                    coding=[
                        Coding(
                            code=code.get("code", None),
                            system=code.get("system", None),
                            display=code.get("display", None),
                        )
                    ]
                )

            elif "alternate_code" in code:
                request.code = CodeableConcept(
                    coding=[
                        Coding(
                            code=code.get("alternate_code", None),
                            system=code.get("alternate_system", None),
                            display=code.get("alternate_display", None),
                        )
                    ]
                )

            entry.append(
                {
                    "resource": request.dumps(exclude_unset=True, exclude_none=True),
                    "request": {"method": "PUT", "url": "ServiceRequest"},
                }
            )

            for observation in observation_request.get("observations", []):
                entry.append(
                    {
                        "resource": prepare_observation(
                            data=observation, parent=request, patient=patient, specimen=None, encounter=None
                        )[0].dumps(exclude_unset=True, exclude_none=True),
                        "request": {"method": "PUT", "url": "Observation"},
                    }
                )

    for observation in observations:
        entry.append(
            {
                "resource": prepare_observation(
                    data=observation, parent=None, patient=patient, specimen=None, encounter=None
                )[0].dumps(exclude_unset=True, exclude_none=True),
                "request": {"method": "PUT", "url": "Observation"},
            }
        )

    print(entry)

    try:
        API.bundle(entry=entry, type="transaction")
    except requests.exceptions.RequestException as e:
        if e.response is not None:
            print(e.response.json())
