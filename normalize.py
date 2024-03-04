"""Normalize the EGP problems list."""
from json import load, dump
from os.path import dirname, join
from typing import Any
from datetime import datetime
from sys import exit as sys_exit

from egp_utils import base_validator
from requests import Response, head


class problem_validator(base_validator):
    """Normalize the EGP problem format."""

    def _normalize_default_setter_set_last_verified_live(self, document) -> str | None:
        """Check the URL is reachable."""
        url: str = document["git_url"] + ("/", "")[document["git_url"].endswith("/")]
        url = (
            url
            + document["git_repo"]
            + ("/commit/", "commit/")[document["git_repo"].endswith("/")]
        )
        url = url + document["git_hash"]
        try:
            response: Response = head(url, allow_redirects=True, timeout=5)
            return (
                datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                if response.status_code == 200
                else document.get("last_verified_live")
            )
        except ConnectionError:
            return document.get("last_verified_live")


with open(
    join(dirname(__file__), "tests/data/problem_format.json"), "r", encoding="utf8"
) as file_ptr:
    EGP_PROBLEM_FORMAT: dict[str, Any] = load(file_ptr)
EGP_PROBLEM_FORMAT["last_verified_live"]["default_setter"] = "set_last_verified_live"


with open(
    join(dirname(__file__), "egp_problems.json"), "r", encoding="utf8"
) as file_ptr:
    EGP_PROBLEMS: list[dict[str, Any]] = load(file_ptr)


validator = problem_validator(EGP_PROBLEM_FORMAT)
for problem in EGP_PROBLEMS:
    if not validator.validate(problem):
        print(problem)
        print(validator.error_str())
        sys_exit(1)
with open(
    join(dirname(__file__), "egp_problems.json"), "w", encoding="utf8"
) as file_ptr:
    dump(
        [validator.normalized(problem) for problem in EGP_PROBLEMS],
        file_ptr,
        indent=4,
        sort_keys=True,
    )
