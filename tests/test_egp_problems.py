"""Test the EGP problem format."""
from json import load
from os.path import dirname, join
from typing import Any

import pytest
from egp_utils import base_validator
from requests import Response, head


with open(join(dirname(__file__), "data/problem_format.json"), "r", encoding="utf8") as file_ptr:
    EGP_PROBLEM_FORMAT: dict[str, Any] = load(file_ptr)
problem_validator = base_validator(EGP_PROBLEM_FORMAT)


with open(join(dirname(__file__), "../egp_problems.json"), "r", encoding="utf8") as file_ptr:
    EGP_PROBLEMS: list[dict[str, Any]] = load(file_ptr)


@pytest.mark.parametrize("problem", EGP_PROBLEMS)
def test_egp_problem_format(problem) -> None:
    """Check the problem format is valid."""
    assert problem_validator.validate(problem)


@pytest.mark.parametrize("problem", EGP_PROBLEMS)
def test_egp_problem_url(problem) -> None:
    """Check the URL is reachable."""
    url: str = problem["git_url"] + ("", "/")[problem["git_url"].endswith("/")]
    url = url + problem["git_repo"] + ("/commit/", "commit/")[problem["git_repo"].endswith("/")]
    url = url + problem["git_hash"]
    try:
        response: Response = head(url, allow_redirects=True, timeout=5)
        assert response.status_code == 200
    except ConnectionError:
        assert False
