import requests
import json

from dotenv import load_dotenv
from os.path import join, dirname

dotenv_path = join(dirname(__file__), "./.env")
load_dotenv(dotenv_path)

from aidbox.resource.allergyintolerance import AllergyIntolerance
from aidbox.resource.observation import Observation
from aidbox.base import API

from aidbox.resource.patient import Patient
from typing import TypedDict

from ADT_A08.observation import prepare_observation
from ADT_A08.patient import prepare_patient
from ADT_A08.allergyintolerance import prepare_allergies
from ADT_A08.encounter import prepare_encounters
from ADT_A08.coverage import prepare_coverage

test = """{
      "visit": {
        "type": "Elective",
        "participant": [
          {
            "name": {
              "given": ["Michael", "L"],
              "family": "Ritchey"
            },
            "type": "attending",
            "identifier": {
              "value": "10895"
            }
          },
          {
            "name": {
              "given": ["Susan", "K"],
              "family": "Burke"
            },
            "type": "referring",
            "identifier": {
              "value": "4074"
            }
          }
        ],
        "reason": {
          "code": "IN PERSON: NP VAGINAL MASS//KS12/18"
        },
        "class": {
          "code": "D"
        },
        "service_type": "7304",
        "identifier": [
          {
            "value": "42700325",
            "system": "visit_number",
            "authority": "Visit"
          }
        ],
        "bed_status": "Clean",
        "hospitalization": {
          "discharge": {
            "disposition": "1"
          },
          "admit_source": "Clinic or Physicians Office^Family Interview"
        },
        "patient_type": "Clinic",
        "v2_accommodation_code": {
          "display": "N"
        },
        "period": {
          "end": ["2021-01-08T23:59:00"],
          "start": "2021-01-08T14:09:29"
        },
        "location": [
          {
            "status": "active",
            "facility": "PCH",
            "point_of_care": "7304"
          }
        ]
      },
      "patient": {
        "address": [
          {
            "city": "PHOENIX",
            "line": ["3931 E GLENROSA AVE"],
            "type": "Home",
            "state": "AZ",
            "county": "MARICOPA",
            "country": "UNITED STATES",
            "postalCode": "85018"
          }
        ],
        "living_will_code": "N",
        "race": [
          {
            "code": "6"
          }
        ],
        "name": [
          {
            "use": "official",
            "given": ["AHEP1531"],
            "family": "TESTPATIENT"
          }
        ],
        "birthDate": "2020-10-14",
        "ethnicity": [
          {
            "code": "4"
          }
        ],
        "account": {
          "identifier": {
            "value": "42700325",
            "authority": "Visit"
          }
        },
        "patient_primary_care_provider_name_id_no_": [
          {
            "name": {
              "given": ["Susan", "K"],
              "family": "Burke"
            },
            "identifier": {
              "value": "4074"
            }
          }
        ],
        "language": {
          "code": "13"
        },
        "marital_status": {
          "code": "6"
        },
        "identifier": [
          {
            "use": "official",
            "value": "6524892",
            "authority": "EMI Primary"
          },
          {
            "value": "6524892",
            "authority": "MRN"
          },
          {
            "value": "UNKNOWN",
            "system": "ssn"
          }
        ],
        "telecom": [
          {
            "use": "home",
            "text": "Cellular",
            "phone": "(602)2953635",
            "system": "phone",
            "area_city": "602",
            "local_number": "2953635"
          },
          {
            "use": "work",
            "text": "Home",
            "phone": "(602)9997471",
            "system": "phone",
            "area_city": "602",
            "local_number": "9997471"
          }
        ],
        "gender": "F"
      },
      "allergies": [
        {
          "code": {
            "code": "Amoxicillin",
            "alternate_code": "d00088",
            "alternate_system": "Multum"
          },
          "type": {
            "code": "Drug"
          },
          "severity": {
            "code": "GI Distress"
          }
        }
      ],
      "diagnosis": [
        {
          "code": {
            "display": "IN PERSON: NP VAGINAL MASS//KS12/18"
          },
          "type": "A"
        },
        {
          "code": {
            "code": "N89.8",
            "system": "ICD10",
            "display": "Other specified noninflammatory disorders of vagina _N89.8"
          },
          "type": "Chronic Issue"
        }
      ],
      "guarantors": [
        {
          "address": [
            {
              "city": "PHOENIX",
              "line": ["3931 E GLENROSA AVE"],
              "state": "AZ",
              "county": "MARICOPA",
              "country": "UNITED STATES",
              "postalCode": "85018"
            }
          ],
          "home_phone": [
            {
              "phone": "(602)2953635",
              "area_city": "602",
              "local_number": "2953635"
            }
          ],
          "identifiers": [
            {
              "value": "4002693",
              "authority": "EMI Primary"
            }
          ],
          "name": [
            {
              "given": ["CHRISTOPHER"],
              "family": "HUNDELT"
            }
          ],
          "work_phone": [
            {
              "phone": "(602)9997471",
              "area_city": "602",
              "local_number": "9997471"
            }
          ],
          "birthDate": "1982-12-03",
          "relationship": {
            "code": "3"
          },
          "type": "I",
          "gender": "M"
        }
      ],
      "insurances": [
        {
          "plan": {
            "type": "COMMERCIAL"
          },
          "group": {
            "id": "282531M004"
          },
          "payor": {
            "address": [
              {
                "city": "PHOENIX",
                "line": ["PO BOX 2924"],
                "text": "BC OUT OF STATE_207_BC OUT OF STATE_0",
                "state": "AZ",
                "country": "UNITED STATES",
                "postalCode": "85062-2924"
              }
            ],
            "contact": {
              "telecom": [
                {
                  "phone": "(602)864-4320",
                  "area_city": "602",
                  "local_number": "864-4320"
                }
              ]
            },
            "identifier": [
              {
                "value": "BCAZOUTSSTND1"
              }
            ],
            "organization": [
              {
                "name": "BLUE CROSS OUT OF STATE 2924",
                "name_type": "Blue Cross"
              }
            ]
          },
          "policy": {
            "identifier": "K3T5346234CH"
          },
          "military": {
            "recipient": {
              "code": "19821203"
            },
            "organization": "M",
            "sponsor_name": [
              {
                "given": ["CHRISTOPHER"],
                "family": "HUNDELT"
              }
            ]
          },
          "beneficiary": {
            "name": [
              {
                "given": ["CHRISTOPHER"],
                "family": "HUNDELT"
              }
            ],
            "gender": "M",
            "address": [
              {
                "city": "PHOENIX",
                "line": ["3931 E GLENROSA AVE"],
                "state": "AZ",
                "county": "MARICOPA",
                "country": "UNITED STATES",
                "postalCode": "85018"
              }
            ],
            "telecom": [
              {
                "use": "home",
                "type": "Phone",
                "phone": "(602)2953635",
                "system": "phone",
                "area_city": "602",
                "local_number": "2953635"
              }
            ],
            "birthDate": "1982-12-03",
            "identifier": [
              {
                "value": "UNKNOWN",
                "system": "ssn"
              }
            ],
            "relationship": {
              "code": "3"
            },
            "subscriber_id": [
              {
                "value": "4002693"
              }
            ]
          },
          "certification": {
            "days": {
              "day_type": "AP",
              "number_of_days": "99"
            },
            "end_date": "2021-12-31",
            "begin_date": "2021-01-07",
            "identifier": {
              "value": "NAR",
              "check_digit": "1170156"
            }
          }
        }
      ],
      "next_of_kins": [
        {
          "name": [
            {
              "given": ["ELIZABETH"],
              "family": "HUNDELT"
            }
          ],
          "address": [
            {
              "city": "PHOENIX",
              "line": ["3931 E GLENROSA AVE"],
              "state": "AZ",
              "county": "MARICOPA",
              "country": "UNITED STATES",
              "postalCode": "85018"
            }
          ],
          "contact_role": {
            "code": "LegallyAuthRep1"
          },
          "phone_number": [
            {
              "text": "Home",
              "phone": "(602)2953635",
              "area_city": "602",
              "local_number": "2953635"
            }
          ],
          "relationship": {
            "code": "18"
          }
        },
        {
          "name": [
            {
              "given": ["CHRISTOPHER"],
              "family": "HUNDELT"
            }
          ],
          "address": [
            {
              "city": "PHOENIX",
              "line": ["3931 E GLENROSA AVE"],
              "state": "AZ",
              "county": "MARICOPA",
              "country": "UNITED STATES",
              "postalCode": "85018"
            }
          ],
          "contact_role": {
            "code": "LegallyAuthRep2"
          },
          "phone_number": [
            {
              "text": "Home",
              "phone": "(602)2953635",
              "area_city": "602",
              "local_number": "2953635"
            }
          ],
          "relationship": {
            "code": "18"
          }
        }
      ],
      "observations": [
        {
          "code": {
            "code": "HEADER1"
          },
          "value": {
            "type": "ST",
            "string": ["Adm Date: 1/8/2021"]
          },
          "status": "X"
        },
        {
          "code": {
            "code": "Primary Language"
          },
          "value": {
            "type": "ST",
            "string": ["Other"]
          },
          "status": "X"
        },
        {
          "code": {
            "code": "1010.3",
            "system": "ClientCharacteristic",
            "display": "HEIGHT",
            "alternate_display": "HEIGHT"
          },
          "value": {
            "TX": ["70"],
            "type": "TX",
            "units": {
              "code": "CM"
            }
          },
          "status": "F",
          "effective": {
            "dateTime": "2021-01-08T14:10:00"
          }
        },
        {
          "code": {
            "code": "1010.1",
            "system": "ClientCharacteristic",
            "display": "WEIGHT",
            "alternate_display": "Current Weight"
          },
          "value": {
            "TX": ["9100"],
            "type": "TX",
            "units": {
              "code": "GM"
            }
          },
          "status": "F",
          "effective": {
            "dateTime": "2021-01-08T14:10:00"
          }
        },
        {
          "code": {
            "code": "1010.1",
            "system": "ClientCharacteristic",
            "display": "WEIGHT",
            "alternate_display": "WEIGHT"
          },
          "value": {
            "TX": ["9100"],
            "type": "TX",
            "units": {
              "code": "GM"
            }
          },
          "status": "F",
          "effective": {
            "dateTime": "2021-01-08T14:10:00"
          }
        },
        {
          "code": {
            "code": "LANGUAGE",
            "system": "ClientCharacteristic"
          },
          "value": {
            "TX": ["English"],
            "type": "TX"
          },
          "status": "F",
          "effective": {
            "dateTime": "2021-01-08T14:10:00"
          }
        }
      ]
}"""


def ADT_08(message):
    entry = []
    patient = prepare_patient(message["patient"])

    if "patient" in message:
        entry.append(
            {
                "resource": patient.model_dump(exclude_unset=True),
                "request": {"method": "POST", "url": "Patient"},
            }
        )

    if "observations" in message:
        for item in message["observations"]:
            entry.append(
                {
                    "resource": prepare_observation(item),
                    "request": {"method": "POST", "url": "Observation"},
                }
            )

    if "allergies" in message:
        for item in message["allergies"]:
            entry.append(
                {
                    "resource": prepare_allergies(item),
                    "request": {"method": "POST", "url": "AllergyIntolerance"},
                }
            )

    if "visit" in message:
        data = prepare_encounters(message["visit"], patient=patient)

        for item in data[0]:
            entry.append(
                {
                    "resource": item.dump(exclude_unset=True),
                    "request": {"method": "PUT", "url": "Location"},
                }
            )

        for item in data[1]:
            entry.append(
                {
                    "resource": item.dump(exclude_unset=True),
                    "request": {"method": "PUT", "url": "Practitioner"},
                }
            )

        entry.append(
            {
                "resource": data[2].dump(exclude_unset=True),
                "request": {"method": "POST", "url": "Encounter"},
            }
        )

    if "insurances" in message:
        for item in message["insurances"]:
            data = prepare_coverage(item, patient)

            entry.append(
                {
                    "resource": data[0].dump(exclude_unset=True),
                    "request": {"method": "PUT", "url": "Organization"},
                }
            )

            entry.append(
                {
                    "resource": data[1].dump(exclude_unset=True),
                    "request": {"method": "POST", "url": "Coverage"},
                }
            )

    try:
        API.bundle(entry=entry, type="transaction")
        print("done!")
    except requests.exceptions.RequestException as e:
        if e.response is not None:
            print(e.response.json())


ADT_08(json.loads(test))


# AllergyIntolerance(patient=Reference(reference="Patient/"))
# pipeline = HL7()
# pipeline.mapping(code="ADT", event="01", worker=hello)
# pipeline.mapping(code="ADT", event="08", worker=hello)

# if ("patient" in parsed_message):
#     patient = Patient()

#     if ("name" in parsed_message):
#         patient.name = [HumanName(**parsed_message["name"])]

#     if ("address" in parsed_message):
#         patient.address = [Address(type="postal")]

#     if ("birthDate" in parsed_message):
#         patient.birthDate = parsed_message.birthDate

# if ("observation" in parsed_message):
