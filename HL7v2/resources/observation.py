from typing import Optional, Union
from aidbox.resource.servicerequest import ServiceRequest
from aidbox.resource.observation import Observation
from aidbox.resource.patient import Patient
from aidbox.resource.organization import Organization
from aidbox.resource.practitionerrole import PractitionerRole
from aidbox.resource.specimen import Specimen
from aidbox.resource.encounter import Encounter
from aidbox.base import (
    CodeableConcept, 
    Coding, 
    Quantity, 
    Identifier,
    Reference,
    Address,
    Annotation,
    Extension,
    Attachment
)

from HL7v2 import get_md5
from HL7v2.resources.utils import convert_datetime_to_utc

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


def get_codes(data):
    codes = []

    match data["code"]:
        case "1010.1":
            codes.append(Coding(
                system="http://loinc.org", code="3141-9", display="Body weight Measured"
            ))
        case "1010.3":
            codes.append(Coding(
                system="http://loinc.org", code="3137-7", display="Body height Measured"
            ))
        case _:
            codes.append(Coding(
                code = data.get("code", None),
                system = data.get("system", None),
                display = data.get("display", None),
                version = data.get("version_id", None)
            ))

    if ("alternate_code" in data) or ("alternate_system" in data) or ("alternate_display" in data):
        codes.append(Coding(
            code = data.get("alternate_code", None),
            system = data.get("alternate_system", None),
            display = data.get("alternate_display", None),
        ))

    return codes


def get_status(status):
    match status:
        case "F":
            return "final"
        case "C":
            return "corrected"
        case "X":
            return "cancelled"
        case _:
            return "registered"


def prepare_observation(
    data, patient: Patient, parent: Optional[Union[Observation, ServiceRequest]], specimen: Specimen, encounter: Encounter
):
    organizations: list[Organization] = []
    practitioner_roles: list[PractitionerRole] = []

    observation = Observation(
        id=get_md5(),
        status=get_status(data.get("status")),
        subject=Reference(reference="Patient/" + (patient.id or "")),
        code=CodeableConcept(coding=get_codes(data["code"])),
        category=[CodeableConcept(coding=[get_category(data)])],
        identifier=[]
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
        observation.effectiveDateTime = convert_datetime_to_utc(data["effective"]["dateTime"])

    if "string" in data.get("value", {}):
        observation.valueString = " ".join(data["value"]["string"])

    if "unit" in data.get("value", {}):
        observation.valueQuantity = Quantity(
            value=data["value"]["TX"], unit=data["value"]["code"]
        )

    if "ED" in data.get("value", {}):
        observation.extension = list(map(lambda attachment_data: Extension(
            url="https://hl7.org/fhir/R5/StructureDefinition/extension-Observation.valueAttachment",
            valueAttachment=Attachment(
                data=attachment_data.get("data"),
                contentType=attachment_data.get("data_subtype")
            )
        ), data.get("value", {}).get("ED", {})))

    if "issued" in data:
        observation.issued = convert_datetime_to_utc(data["issued"])

    if "performer" in data:
        observation.performer = []

    if "organization" in data.get("performer", {}):
        organization_data = data["performer"]["organization"]

        organization = Organization(
            id=get_md5([organization_data["identifier"]]),
            name=organization_data["name"],
            identifier=[Identifier(
                system=organization_data["authority"],
                type=CodeableConcept(coding=[Coding(code=organization_data["type"])]),
                value=organization_data["identifier"]
            )]
        )

        if "address" in data["performer"]:
            organization.address = [Address(
                line=data["performer"]["address"]["line"],
                city=data["performer"]["address"]["city"],
                state=data["performer"]["address"]["state"],
                postalCode=data["performer"]["address"]["postalCode"]
            )]

        observation.performer.append(Reference(reference="Organization/" + organization.id))

        organizations.append(organization)

    if "access_checks" in data:
        observation.note = [Annotation(text=data["access_checks"])]

    if "responsible" in data.get("performer", {}):
        responsibles_data = data["performer"]["responsible"]

        for responsible_data in responsibles_data:
            responsible_identifier = responsible_data.get("identifier", {})

            practitioner_role = PractitionerRole(
                id=get_md5(),
                practitioner=Reference(
                    type="Practitioner",
                    identifier=Identifier(
                        value=responsible_identifier["value"]
                    )
                ),
                code=[CodeableConcept(coding=[Coding(
                    system="http://terminology.hl7.org/CodeSystem/practitioner-role",
                    code="responsibleObserver"
                )])]
            )

            observation.performer.append(Reference(reference="PractitionerRole/" + practitioner_role.id))

            practitioner_roles.append(practitioner_role)

    if specimen is not None:
        observation.focus = [Reference(reference="Specimen/" + specimen.id)]

    if encounter is not None:
        observation.encounter = Reference(reference="Encounter/" + encounter.id)

    return (observation, organizations, practitioner_roles)
