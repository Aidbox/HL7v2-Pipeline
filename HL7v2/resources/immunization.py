import datetime

from aidbox.resource.immunization import (
    Immunization,
    Immunization_ProtocolApplied,
)

from aidbox.resource.patient import Patient

from aidbox.base import (
    Reference,
    CodeableConcept,
    Coding,
    Quantity,
)

def prepare_immunization(data, patient: Patient) -> Immunization:
    immunization = Immunization(
        status = "completed",
        patient = Reference(
            reference = "Patient/" + (patient.id or "")
        ),
        vaccineCode = CodeableConcept(
            coding = [
                Coding(
                    system = data["administered_code"]["system"],
                    code = data["administered_code"]["code"],
                    display = data["administered_code"]["display"]
                )
            ]
        )
    )

    if "datetime_start_of_administration" in data:
        immunization.occurrenceDateTime = data["datetime_start_of_administration"] + "Z"
    else:
        immunization.occurrenceDateTime = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()

    if "administration_site" in data:
        immunization.site = CodeableConcept(
            coding = [
                Coding(
                    system = data["administration_site"]["system"],
                    code = data["administration_site"]["code"],
                    display = data["administration_site"]["display"]
                )
            ]
        )
        
    if "substance_lot_number" in data:
        immunization.lotNumber = data["substance_lot_number"]

    if "route" in data:
        immunization.route = CodeableConcept(
            coding = [
                Coding(
                    system=  data["route"]["system"],
                    code = data["route"]["code"],
                    display = data["route"]["display"],
                )
            ]
        )

    if "administration_sub_id_counter" in data:
        immunization.protocolApplied = [
            Immunization_ProtocolApplied(
                doseNumberPositiveInt = int(data["administration_sub_id_counter"])
            )
        ]

    if "substance_manufacturer_name" in data:
        immunization.manufacturer = Reference(
            display = data["substance_manufacturer_name"]["display"]
        )

    if "administered_amount" in data:
        immunization.doseQuantity = Quantity(
            system = "http://unitsofmeasure.org",
            value = 20,
            code = "mg"
        )

    if "substance_expiration_date" in data:
        immunization.expirationDate = data["substance_expiration_date"]

    return immunization
