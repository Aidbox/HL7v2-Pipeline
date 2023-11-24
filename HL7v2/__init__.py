import hashlib


def get_md5(strings: list[str | None]):
    data: list[str] = []

    for s in strings:
        if s is not None:
            data.append(s)

    return hashlib.md5("".join(data).encode("utf-8")).hexdigest()


def pop_string(data: list[str] | str | None):
    if isinstance(data, list):
        return data.pop()

    if isinstance(data, str):
        return data

    return ""


def get_resource_id(data):
    if "patient" in data:
        if "identifier" in data["patient"]:
            official = next(
                (
                    item
                    for item in data["patient"]["identifier"]
                    if item.get("use") == "official"
                ),
                None,
            )
            if official is not None:
                return get_md5([official["value"]])

    return get_md5([""])
