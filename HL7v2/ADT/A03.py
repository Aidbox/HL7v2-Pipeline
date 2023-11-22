# ADT Discharge Message
# An A03 event signals the end of a patient's stay in a healthcare facility.
# It signals that the patient's status has changed to "discharged" and that a discharge date has been recorded.
# The patient is no longer in the facility.
# The patient's location prior to discharge should be entered in PV1-3 - Assigned Patient Location.


def run(message):
    entry = []
