import hashlib
import random, string, hashlib, argparse, sys


def random_md5():
    random_string = "".join(random.choices(string.ascii_letters + string.digits, k=10))
    return hashlib.md5(random_string.encode()).hexdigest()


def get_md5(strings: list[str | None] = []):
    data: list[str] = []

    if len(strings) == 0 or all(element is None for element in strings):
        return random_md5()

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
