from typing import NamedTuple
from unittest.mock import MagicMock

import pytest
from micropy import MicroPy, logger
from micropy.project import Project
from micropy.stubs import StubManager
from pytest_mock import MockFixture
from typer.testing import CliRunner


@pytest.fixture()
def runner():
    runner = CliRunner()
    with runner.isolated_filesystem():
        yield runner


class MicroPyScenario(NamedTuple):
    project_exists: bool = True
    has_stubs: bool = True


@pytest.fixture()
def micropy_obj(request: pytest.FixtureRequest, tmp_path, mocker: MockFixture) -> MicroPy:
    mpy = mocker.MagicMock(MicroPy, autospec=True)
    mpy.log = logger.Log.add_logger("MicroPy")
    mpy.project = mocker.MagicMock(Project, autospec=True).return_value
    mpy.stubs = mocker.MagicMock(StubManager, autospec=True).return_value
    mpy.stubs.add = lambda i: i
    if param := getattr(request, "param", MicroPyScenario()):
        mpy.project.exists = param.project_exists
        stubs = ["a-stub"] if param.has_stubs else []
        mpy.stubs.__iter__.return_value = iter(stubs)
    mocker.patch("micropy.main.MicroPy", return_value=mpy)
    return mpy


@pytest.fixture(params=[True, False])
def context_mock(request: pytest.FixtureRequest, mocker: MockFixture, micropy_obj) -> MagicMock:
    ctx = mocker.MagicMock()
    ctx.ensure_object.return_value = micropy_obj
    ctx.find_object.return_value = micropy_obj
    ctx.resilient_parsing = request.param
    ctx.obj = micropy_obj
    return ctx
