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

from ADT_A08.utils import get_md5, pop_string


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
        class_=get_code(data["patient_type"]),
        subject=Reference(reference="Patient/" + (patient.id or "")),
    )

    if "period" in data:
        encounter.period = Period(
            start=pop_string(data["period"]["start"]),
            end=pop_string(data["period"]["end"]),
        )

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
                    id=get_md5([item["facility"], item["point_of_care"]]),
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
        practitioners = list(
            map(
                lambda item: Practitioner(
                    id=get_md5([item["identifier"]["value"]]),
                    name=[HumanName(**item["name"])],
                    identifier=[Identifier(id=item["identifier"]["value"])],
                ),
                data["participant"],
            )
        )

        encounter.participant = list(
            map(
                lambda item: Encounter_Participant(
                    individual=Reference(reference="Practitioner/" + (item.id or ""))
                ),
                practitioners,
            )
        )

    return (locations, practitioners, encounter)
