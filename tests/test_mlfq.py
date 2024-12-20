from pathlib import Path
import pytest
from pytest import CaptureFixture

@pytest.mark.parametrize("inputpath", ["tests/testcase1.txt"])
def test_case1(inputpath,get_controller, capsys) -> None: #type:ignore
    get_controller.run(inputpath) #type:ignore
    result:CaptureFixture[str] = capsys.readouterr() #type:ignore
    with open(Path("tests/expected1.txt")) as expected:
        assert expected.readlines() == out.splitlines(keepends=True) #type:ignore
