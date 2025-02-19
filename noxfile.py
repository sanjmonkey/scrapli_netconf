"""scrapli_netconf.noxfile"""
import re
import sys
from pathlib import Path
from typing import Dict, List

import nox

nox.options.error_on_missing_interpreters = False
nox.options.stop_on_first_error = False
nox.options.default_venv_backend = "venv"


def parse_requirements(dev: bool = True) -> Dict[str, str]:
    """
    Parse requirements file

    Args:
        dev: parse dev requirements (or not)

    Returns:
        dict: dict of parsed requirements

    Raises:
        N/A

    """
    requirements = {}
    requirements_file = "requirements.txt" if not dev else "requirements-dev.txt"

    with open(requirements_file, "r", encoding="utf-8") as f:
        requirements_file_lines = f.readlines()

    requirements_lines: List[str] = [
        line
        for line in requirements_file_lines
        if not line.startswith("-r") and not line.startswith("#") and not line.startswith("-e")
    ]
    editable_requirements_lines: List[str] = [
        line for line in requirements_file_lines if line.startswith("-e")
    ]

    for requirement in requirements_lines:
        parsed_requirement = re.match(
            pattern=r"^([a-z0-9\-\_\.\[\]]+)([><=]{1,2}\S*)(?:.*)$",
            string=requirement,
            flags=re.I | re.M,
        )
        requirements[parsed_requirement.groups()[0]] = parsed_requirement.groups()[1]

    for requirement in editable_requirements_lines:
        parsed_requirement = re.match(
            pattern=r"^-e\s.*(?:#egg=)(\w+)$", string=requirement, flags=re.I | re.M
        )
        requirements[parsed_requirement.groups()[0]] = requirement

    return requirements


REQUIREMENTS: Dict[str, str] = parse_requirements(dev=False)
DEV_REQUIREMENTS: Dict[str, str] = parse_requirements(dev=True)
PLATFORM: str = sys.platform
SKIP_LIST: List[str] = [
    "integration_tests-darwin-3.11",
]


@nox.session(python=["3.7", "3.8", "3.9", "3.10", "3.11"])
def unit_tests(session):
    """
    Nox run unit tests

    Args:
        session: nox session

    Returns:
        None

    Raises:
        N/A

    """
    if f"unit_tests-{PLATFORM}-{session.python}" in SKIP_LIST:
        return

    session.install("-U", "setuptools", "wheel", "pip")
    session.install(".[dev]")
    session.run(
        "python",
        "-m",
        "pytest",
        "--cov=scrapli_netconf",
        "--cov-report",
        "xml",
        "--cov-report",
        "term",
        "tests/unit",
        "-v",
    )


@nox.session(python=["3.11"])
def isort(session):
    """
    Nox run isort

    Args:
        session: nox session

    Returns:
        None

    Raises:
        N/A

    """
    session.install(f"toml{DEV_REQUIREMENTS['toml']}")
    session.install(f"isort{DEV_REQUIREMENTS['isort']}")
    session.run("python", "-m", "isort", "-c", ".")


@nox.session(python=["3.11"])
def black(session):
    """
    Nox run black

    Args:
        session: nox session

    Returns:
        None

    Raises:
        N/A

    """
    session.install(f"toml{DEV_REQUIREMENTS['toml']}")
    session.install(f"black{DEV_REQUIREMENTS['black']}")
    session.run("python", "-m", "black", "--check", ".")


@nox.session(python=["3.11"])
def pylama(session):
    """
    Nox run pylama

    Args:
        session: nox session

    Returns:
        None

    Raises:
        N/A

    """
    session.install(".[dev]")
    session.run("python", "-m", "pylama", ".")


@nox.session(python=["3.11"])
def pydocstyle(session):
    """
    Nox run pydocstyle

    Args:
        session: nox session

    Returns:
        None

    Raises:
        N/A

    """
    session.install(f"toml{DEV_REQUIREMENTS['toml']}")
    session.install(f"pydocstyle{DEV_REQUIREMENTS['pydocstyle']}")
    session.run("python", "-m", "pydocstyle", ".")


@nox.session(python=["3.11"])
def mypy(session):
    """
    Nox run mypy

    Args:
        session: nox session

    Returns:
        None

    Raises:
        N/A

    """
    session.install(".")
    session.install(f"toml{DEV_REQUIREMENTS['toml']}")
    session.install(f"mypy{DEV_REQUIREMENTS['mypy']}")
    session.run("python", "-m", "mypy", "--strict", "scrapli_netconf/")


@nox.session(python=["3.11"])
def darglint(session):
    """
    Nox run darglint

    Args:
        session: nox session

    Returns:
        None

    Raises:
        N/A

    """
    session.install(f"darglint{DEV_REQUIREMENTS['darglint']}")
    for file in Path("scrapli_netconf").rglob("*.py"):
        session.run("darglint", f"{file.absolute()}")
