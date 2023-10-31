from aidbox.resource.allergyintolerance import AllergyIntolerance
from aidbox.base import Reference, CodeableConcept, Coding


def get_category(code):
    match code:
        case "Drug":
            return "medication"
        case _:
            return "environment"


def get_code(code):
    match code["code"]:
        case "Amoxicillin":
            return Coding(
                system="http://snomed.info/sct",
                code="294505008",
                display="Allergy to Amoxicillin",
            )
        case _:
            return Coding()


def prepare_allergies(data):
    allergy = AllergyIntolerance(
        patient=Reference(reference="Patient/"),
        clinicalStatus=CodeableConcept(
            coding=[
                Coding(
                    system="http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                    code="active",
                )
            ]
        ),
        code=CodeableConcept(coding=[get_code(data)]),
    )

    if "type" in data:
        allergy.category = [get_category(data["type"]["code"])]

    return allergy.dumps(exclude_unset=True)
