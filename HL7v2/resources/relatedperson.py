from aidbox.resource.relatedperson import RelatedPerson, RelatedPerson_Communication
from aidbox.resource.patient import Patient
from aidbox.base import Reference, HumanName, CodeableConcept, Coding
from aidbox.base import (
    HumanName,
    ContactPoint,
    Address,
    Identifier,
    CodeableConcept,
    Coding,
)


def get_gender_by_code(code):
    match code:
        case "F":
            return "female"
        case "M":
            return "male"
        case _:
            return "unknown"


def get_relationship(coding):
    system = "http://terminology.hl7.org/CodeSystem/v2-0131"

    match coding["code"]:
        case "NK":
            return Coding(code="N", system=system)
        case _:
            return Coding(**coding)


def get_role(coding):
    system = "http://terminology.hl7.org/CodeSystem/v3-RoleCode"

    match coding["code"]:
        case "":
            return Coding(code="SPS", system=system)
        case _:
            return Coding(**coding)


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


def prepare_related_persons(data, patient: Patient):
    person = RelatedPerson(
        patient=Reference(reference="Patient/" + (patient.id or "")),
        relationship=[]
    )

    if "name" in data:
        person.name = list(map(lambda item: HumanName(**item), data["name"]))

    if "birthDate" in data:
        person.birthDate = data["birthDate"]

    if "gender" in data:
        person.gender = get_gender_by_code(person.gender)

    if "address" in data:
        person.address = list(
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
        person.telecom = list(map(lambda item: ContactPoint(**item), data["telecom"]))

    if "identifier" in data:
        person.identifier = list(
            map(lambda item: Identifier(**item), data["identifier"])
        )

    if "language" in data:
        person.communication = [
            RelatedPerson_Communication(
                language=CodeableConcept(
                    coding=[get_language_by_code(data["language"])]
                )
            )
        ]

    if "relationship" in data:
        person.relationship.append(
            CodeableConcept(coding=[get_relationship(data["relationship"])])
        )

    if "contact_role" in data:
        person.relationship.append(CodeableConcept())

    return person.dumps(exclude_none=True, exclude_unset=True)
