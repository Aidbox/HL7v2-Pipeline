from aidbox.resource.encounter import (
    Encounter,
    Encounter_Location,
    Encounter_Participant,
)
from aidbox.resource.location import Location
from aidbox.resource.patient import Patient
from aidbox.resource.practitioner import Practitioner
from aidbox.base import (
    CodeableConcept,
    Coding,
    Reference,
    Period,
    Identifier,
    HumanName,
)

from HL7v2 import get_md5, pop_string


def get_code(type):
    if type == "Clinic":
        return Coding(
            code="IMP", system="http://terminology.hl7.org/ValueSet/v3-ActEncounterCode"
        )

    return Coding(
        code="NONAC", system="http://terminology.hl7.org/ValueSet/v3-ActEncounterCode"
    )


def prepare_encounters(
    data, patient: Patient
) -> tuple[list[Location], list[Practitioner], Encounter]:
    locations: list[Location] = []
    practitioners: list[Practitioner] = []
    encounter = Encounter(
        status="finished",
        class_=get_code(data.get("patient_type", "")),
        subject=Reference(reference="Patient/" + (patient.id or "")),
    )

    if "period" in data:
        period = data.get("period", {})
        encounter.period = Period()
        start = pop_string(period.get("start"))
        end = pop_string(period.get("end"))

        if start:
            encounter.period.start = start + "Z"
        if end:
            encounter.period.end = start + "Z"

    if "indentifier" in data:
        for item in data["identifier"]:
            encounter.identifier.append(
                Identifier(system=item["system"], value=item["value"])
            )

    if "reason" in data:
        encounter.reasonCode = [
            CodeableConcept(coding=[Coding(code=data["reason"]["code"])])
        ]

    if "location" in data:
        locations = list(
            map(
                lambda item: Location(
                    status=item["status"],
                    id=get_md5(
                        [item.get("facility", ""), item.get("point_of_care", "")]
                    ),
                ),
                data["location"],
            )
        )

        encounter.location = list(
            map(
                lambda item: Encounter_Location(
                    location=Reference(reference="Location/" + (item.id or ""))
                ),
                locations,
            )
        )

    if "participant" in data:
        for participant in data["participant"]:
            data_name = participant.get("name", {})
            name = HumanName()
            identifier = participant.get("identifier", {}).get("value", None)
            practitioner = Practitioner(
                id=get_md5([participant.get("identifier", {}).get("value", None)]),
                name=[name],
            )

            if "given" in data_name:
                name.given = data_name["given"]

            if "family" in data_name:
                name.family = data_name["family"]

            if "prefix" in data_name:
                name.prefix = [data_name["prefix"]]

            if identifier is not None:
                practitioner.identifier = [Identifier(value=identifier)]

            practitioners.append(practitioner)

        encounter.participant = list(
            map(
                lambda item: Encounter_Participant(
                    individual=Reference(reference="Practitioner/" + (item.id or ""))
                ),
                practitioners,
            )
        )

    return (locations, practitioners, encounter)
