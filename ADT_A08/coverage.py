from aidbox.resource.coverage import Coverage
from aidbox.resource.patient import Patient
from aidbox.resource.organization import Organization

from aidbox.base import Reference, Period, Address, ContactPoint, Identifier
from ADT_A08.utils import get_md5


def get_contact_point(telecom):
    if "phone" in telecom:
        return ContactPoint(system="phone", value=telecom["phone"])

    if "email" in telecom:
        return ContactPoint(system="email", value=telecom["email"])

    return ContactPoint(system=telecom["system"], value=telecom["value"])


def prepare_coverage(data, patient: Patient):
    organization = Organization(
        id=get_md5([]),
        identifier=list(
            map(lambda item: Identifier(**item), (data["payor"]["identifier"] or []))
        ),
        name=data["payor"]["organization"][0]["name"],
        address=list(
            map(lambda item: Address(**item), (data["payor"]["address"] or []))
        ),
        telecom=list(
            map(
                lambda item: get_contact_point(item),
                (data["payor"]["contact"]["telecom"] or []),
            )
        ),
    )

    coverage = Coverage(
        status="active",
        beneficiary=Reference(reference="Patient/" + (patient.id or "")),
        payor=[Reference(reference="Organization/" + (organization.id or ""))],
    )

    if "certification" in data:
        coverage.period = Period(
            start=data["certification"]["begin_date"],
            end=data["certification"]["end_date"],
        )

    return (organization, coverage)
