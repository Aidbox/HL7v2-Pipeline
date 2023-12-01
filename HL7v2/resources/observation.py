from typing import Optional, Union
from aidbox.resource.servicerequest import ServiceRequest
from aidbox.resource.observation import Observation
from aidbox.resource.patient import Patient
from aidbox.base import CodeableConcept, Coding, Quantity, Identifier, Reference

from HL7v2 import get_md5


def get_category(data):
    if data["code"]["code"] in ["1010.1", "1010.3"]:
        return Coding(
            system="http://terminology.hl7.org/CodeSystem/observation-category",
            code="vital-signs",
        )

    return Coding(
        system="http://terminology.hl7.org/CodeSystem/observation-category",
        code="social-history",
    )


def get_code(data):
    match data["code"]:
        case "1010.1":
            return Coding(
                system="http://loinc.org", code="3141-9", display="Body weight Measured"
            )
        case "1010.3":
            return Coding(
                system="http://loinc.org", code="3137-7", display="Body height Measured"
            )
        case _:
            return Coding(code=data["code"])


def get_status(status):
    match status:
        case "F":
            return "final"
        case _:
            return "registered"


def prepare_observation(
    data, patient: Patient, parent: Optional[Union[Observation, ServiceRequest]]
):
    observation = Observation(
        id=get_md5([]),
        status=get_status(data["status"]),
        subject=Reference(reference="Patient/" + (patient.id or "")),
        code=CodeableConcept(coding=[get_code(data["code"])]),
        category=[CodeableConcept(coding=[get_category(data)])],
    )

    if parent:
        resourceType = parent.__class__.__name__
        observation.hasMember = [
            Reference(reference=resourceType + "/" + (parent.id or ""))
        ]

    if data.get("identifier", {}).get("filler_number"):
        observation.identifier.append(
            Identifier(
                system="filler_number",
                value=data["identifier"]["filler_number"].get("identifier"),
            )
        )

    if data.get("identifier", {}).get("placer_number"):
        observation.identifier.append(
            Identifier(
                system="placer_number",
                value=data["identifier"]["placer_number"].get("identifier"),
            )
        )

    if "effective" in data:
        observation.effectiveDateTime = data["effective"]["dateTime"] + "Z"

    if "string" in data["value"]:
        observation.valueString = " ".join(data["value"]["string"])

    if "unit" in data["value"]:
        observation.valueQuantity = Quantity(
            value=data["value"]["TX"], unit=data["value"]["code"]
        )

    return observation
