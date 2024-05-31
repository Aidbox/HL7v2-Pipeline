from aidbox.resource.diagnosticreport import DiagnosticReport
from aidbox.resource.practitionerrole import PractitionerRole
from aidbox.resource.patient import Patient
from aidbox.resource.encounter import Encounter
from aidbox.resource.specimen import Specimen, Specimen_Collection

from HL7v2 import get_md5
from HL7v2.resources.observation import prepare_observation
from HL7v2.resources.utils import convert_datetime_to_utc, get_codings

from aidbox.base import (
    Reference,
    CodeableConcept,
    Coding,
    Identifier,
    Extension
)

def get_status(code):
    match code:
        case "CA" | "DC":
            return "cancelled"
        case "SC":
            return "corrected"
        case "HD" | "IP" | "SC":
            return "registered"
        case "A":
            return "preliminary"
        case "CM":
            return "final"
        case "ER":
            return "entered-in-error"
        case _:
            return "unknown"

def prepare_diagnostic_report(data, patient: Patient, encounter: Encounter, parent: DiagnosticReport) -> (DiagnosticReport, list[PractitionerRole]):
    practitioner_roles: list[PractitionerRole] = []
    observations: list[Observations] = []

    diagnostic_report = parent or DiagnosticReport(
        id=get_md5(),
        status=get_status(data.get("status", {}).get("code")),
        code=CodeableConcept(coding=[]),
        result=[]
    )

    if (parent is None) and ("identifier" in data):
        identifier_data = data.get("identifier", {}).get("filler_number", {})

        diagnostic_report.id = get_md5([identifier_data["identifier"]])

        diagnostic_report.identifier = [Identifier(
            id=get_md5(),
            type=CodeableConcept(coding=[Coding(
                system="http://terminology.hl7.org/CodeSystem/v2-0203",
                code="FILL"
            )]),
            value=identifier_data["identifier"]
        )]

    if (parent is not None) and ("parent_uid" in data):
        diagnostic_report.code = CodeableConcept(coding=get_codings(data.get("parent_uid")))

    if (parent is not None) and ("diagnostic_service" in data):
        diagnostic_report.category = [CodeableConcept(coding=[Coding(
            code=data["diagnostic_service"]
        )])]

    if (parent is not None) and ("result_status_change_datetime" in data):
        diagnostic_report.issued = convert_datetime_to_utc(data["result_status_change_datetime"])

    if (parent is not None) and ("principal_interpreter" in data):
        practitioner_role = PractitionerRole(
            id=get_md5(),
            practitioner=Reference(
                type="Practitioner",
                identifier=Identifier(
                    value=data.get("principal_interpreter", {}).get("name", {}).get("id")
                )
            )
        )

        practitioner_roles.append(practitioner_role)

        diagnostic_report.resultsInterpreter = [Reference(reference="PractitionerRole/" + practitioner_role.id)]

    if (parent is not None) and ("technician" in data):
        practitioner_role = PractitionerRole(
            id=get_md5(),
            practitioner=Reference(
                extension=[Extension(
                    url="http://hl7.org/fhir/StructureDefinition/event-performerFunction",
                    valueCodeableConcept=CodeableConcept(coding=[Coding(
                        system="http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                        code="SPRF"
                    )])
                )],
                type="Practitioner",
                identifier=Identifier(
                    value=data.get("technician", [])[0].get("name", {}).get("id")
                )
            )
        )

        practitioner_roles.append(practitioner_role)

        diagnostic_report.performer = [Reference(reference="PractitionerRole/" + practitioner_role.id)]

    if (parent is not None) and ("specimens" in data):
        for specimen_data in data["specimens"]:
            specimen = Specimen(
                id=get_md5()
            )

            specimen_identifier_data = specimen_data.get("id", {}).get("filler_id", {})

            if "identifier" in specimen_identifier_data:
                specimen.id = get_md5([specimen_identifier_data.get("identifier")])

                specimen.identifier = [Identifier(
                    type=CodeableConcept(coding=[Coding(
                        system="http://terminology.hl7.org/CodeSystem/v2-0203",
                        code="PGN"
                    )]),
                    value=specimen_identifier_data.get("identifier")
                )]

            if "method" in specimen_data:
                specimen.collection = Specimen_Collection(
                    method=CodeableConcept(
                        coding=get_codings(specimen_data.get("method"))
                    )
                )

            if "observations" in specimen_data:
                for observation_data in specimen_data.get("observations"):
                    observations.append(prepare_observation(observation_data, patient=patient, parent=None, specimen=specimen, encounter=encounter)[0])

    return (diagnostic_report, practitioner_roles, observations)
