from aidbox.resource.patient import Patient
from aidbox.resource.condition import Condition

from aidbox.base import Reference, CodeableConcept, Coding, Annotation


def prepare_condition(data, patient: Patient):
    condition = Condition(subject=Reference(reference="Patient/" + (patient.id or "")))

    if "code" in data:
        code = data["code"]
        condition.code = CodeableConcept(
            coding=[
                Coding(
                    code=code.get("code", None),
                    system=code.get("system", None),
                    display=code.get("display", None),
                )
            ]
        )

    return condition.dumps(exclude_none=True, exclude_unset=True)
