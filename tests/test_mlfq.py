from pathlib import Path
import pytest

TESTCASENUM = 6

@pytest.mark.parametrize("testcase_num", [i for i in range(1,TESTCASENUM+1)])
def test_correctness(testcase_num,get_controller, capsys) -> None: #type:ignore
    get_controller.run(f"tests/testcase{testcase_num}.txt") #type:ignore
    out, _ = capsys.readouterr() #type:ignore
    with open(Path(f"tests/expected{testcase_num}.txt"),"r") as expected:
        assert expected.readlines() == out.splitlines(keepends=True) #type:ignore


