from aidbox.resource.observation import Observation
from aidbox.base import CodeableConcept, Coding, Quantity


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


def prepare_observation(data):
    observation = Observation(
        status=get_status(data["status"]),
        code=CodeableConcept(coding=[get_code(data["code"])]),
        category=[CodeableConcept(coding=[get_category(data)])],
    )

    if "effective" in data:
        observation.effectiveDateTime = data["effective"]["dateTime"]

    if "string" in data["value"]:
        observation.valueString = " ".join(data["value"]["string"])

    if "unit" in data["value"]:
        observation.valueQuantity = Quantity(
            value=data["value"]["TX"], unit=data["value"]["code"]
        )

    return observation.model_dump(exclude_unset=True)
