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
from HL7v2.resources.utils import convert_datetime_to_utc

def get_code(type):
    if type == "O":
        return Coding(
            system = "http://terminology.hl7.org/ValueSet/v3-ActEncounterCode",
            code = "AMB",
        )

    if type == "E":
        return Coding(
            system = "http://terminology.hl7.org/ValueSet/v3-ActEncounterCode",
            code = "EMER",
        )

    if type == "I":
        return Coding(
            system = "http://terminology.hl7.org/ValueSet/v3-ActEncounterCode",
            code = "IMP",
        )

    if type == "P":
        return Coding(
            system = "http://terminology.hl7.org/ValueSet/v3-ActEncounterCode",
            code = "PRENC",
        )

    if type == "R":
        return Coding(
            system = "http://terminology.hl7.org/CodeSystem/v2-0004",
            code = "R",
        )

    if type == "B":
        return Coding(
            system = "http://terminology.hl7.org/CodeSystem/v2-0004",
            code = "B",
        )

    if type == "C":
        return Coding(
            system = "http://terminology.hl7.org/CodeSystem/v2-0004",
            code = "C",
        )

    if type == "N":
        return Coding(
            system = "http://terminology.hl7.org/CodeSystem/v2-0004",
            code = "N",
        )

    if type == "U":
        return Coding(
            system = "http://terminology.hl7.org/CodeSystem/v2-0004",
            code = "U",
        )

    if type == "Clinic":
        return Coding(
            system = "http://terminology.hl7.org/ValueSet/v3-ActEncounterCode",
            code = "IMP",
        )

    return Coding(
        system = "http://terminology.hl7.org/ValueSet/v3-ActEncounterCode",
        code = "NONAC"
    )

def get_use(use):
    match use:
        case "L":
            return "official"
        case _:
            return None

def prepare_encounters(
    data, patient: Patient
) -> tuple[list[Location], list[Practitioner], Encounter]:
    visit_data = data["visit"]
    patient_data = data["patient"]

    locations: list[Location] = []
    practitioners: list[Practitioner] = []
    encounter = Encounter(
        id=get_md5(),
        status="finished",
        class_=get_code(visit_data.get("patient_type", "") or visit_data.get("class", {}).get("code", "")),
        subject=Reference(reference="Patient/" + (patient.id or "")),
    )

    if "period" in visit_data:
        period = visit_data.get("period", {})
        encounter.period = Period()
        start = pop_string(period.get("start"))
        end = pop_string(period.get("end"))

        if start:
            encounter.period.start = convert_datetime_to_utc(start)
        if end:
            encounter.period.end = convert_datetime_to_utc(end)

    if "identifier" in visit_data:
        patient_identifier = patient_data.get("account", {}).get("identifier", {})

        encounter.identifier = list(map(lambda item: Identifier(system=item["system"], value=(patient_identifier.get("value", None) or item["value"])), visit_data["identifier"]))

    if "reason" in visit_data:
        encounter.reasonCode = [
            CodeableConcept(coding=[Coding(code=visit_data["reason"]["code"])])
        ]

    if "location" in visit_data:
        locations = list(
            map(
                lambda item: Location(
                    status=item["status"],
                    id=get_md5(
                        [item.get("facility", ""), item.get("point_of_care", "")]
                    ),
                    description = item.get("location_description", None)
                ),
                visit_data["location"],
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

    if "participant" in visit_data:
        for participant in visit_data["participant"]:
            data_name = participant.get("name", {})
            name = HumanName()
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

            if "use" in data_name:
                name.use = get_use(data_name["use"])

            if "identifier" in participant:
                identifier_value = participant["identifier"].get("value", None)
                identifier_system = participant["identifier"].get("system", None)
                practitioner.identifier = [Identifier(system=identifier_system, value=identifier_value)]

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
