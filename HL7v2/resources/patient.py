from aidbox.resource.patient import Patient, Patient_Communication
from aidbox.resource.appointment import Appointment
from aidbox.base import (
    HumanName,
    ContactPoint,
    Address,
    Identifier,
    CodeableConcept,
    Coding,
    Extension,
    Meta,
)

from HL7v2 import get_resource_id


def get_gender_by_code(code):
    match code:
        case "F":
            return "female"
        case "M":
            return "male"
        case _:
            return "unknown"


def get_marital_status_code(code):
    system = "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus"

    match code:
        case "1":
            return Coding(system=system, code="A", display="Annulled")
        case "13":
            return Coding(system=system, code="M", display="Married")
        case _:
            return Coding(system=system, code="UNK", display="unknown")


def get_language_by_code(code):
    system = "http://hl7.org/fhir/ValueSet/languages"

    match code:
        case "13":
            return Coding(system=system, code="pl-PL", display="Polish (Poland)")
        case "27":
            return Coding(system=system, code="zh-CN", display="Chinese (China)")
        case _:
            return Coding(
                system=system, code="en-US", display="English (United States)"
            )


def prepare_patient(data):
    patient = Patient(id=get_resource_id({"patient": data}))

    if "name" in data:
        patient.name = list(map(lambda item: HumanName(**item), data["name"]))

    if "birthDate" in data:
        patient.birthDate = data["birthDate"]

    if "gender" in data:
        patient.gender = get_gender_by_code(data["gender"])

    if "address" in data:
        patient.address = list(
            map(
                lambda item: Address(
                    use=item.get("use", "work").lower(),
                    city=item.get("city", None),
                    state=item.get("state", None),
                    country=item.get("country", None),
                    line=item.get("line", []),
                    postalCode=item.get("postalCode", None),
                ),
                data["address"],
            )
        )

    if "telecom" in data:
        patient.telecom = list(
            map(
                lambda item: ContactPoint(use="home", value=item.get("phone", "")),
                data.get("telecom", []),
            )
        )

    if "identifier" in data:
        patient.identifier = list(
            map(lambda item: Identifier(**item), data["identifier"])
        )

    if "marital_status" in data:
        patient.maritalStatus = CodeableConcept(coding=[get_marital_status_code(data)])

    if "language" in data:
        patient.communication = [
            Patient_Communication(
                language=CodeableConcept(
                    coding=[get_language_by_code(data["language"])]
                )
            )
        ]

    return patient
