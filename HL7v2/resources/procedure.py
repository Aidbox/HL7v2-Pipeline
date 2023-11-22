from aidbox.resource.patient import Patient
from aidbox.resource.procedure import Procedure

from aidbox.base import Reference, CodeableConcept, Coding, Annotation


def prepare_procedure(data, patient: Patient):
    procedure = Procedure(
        status="completed",
        subject=Reference(reference="Patient/" + (patient.id or "")),
    )

    if "procedure_datetime" in data:
        procedure.performedDateTime = data["procedure_datetime"]

    if "procedure_code" in data:
        code = data.get("procedure_code", {})
        procedure.code = CodeableConcept(
            coding=[Coding(code=code.get("code", ""), display=code.get("display", ""))]
        )

    if "procedure_description" in data:
        procedure.note = [Annotation(text=data.get("procedure_description", ""))]

    return procedure.dumps(exclude_unset=True)
