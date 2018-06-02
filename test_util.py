
from util import weekday_offset

def test_next_wednesday():
    assert weekday_offset(1, 3) == 2
    assert weekday_offset(2, 3) == 1
    assert weekday_offset(3, 3) == 7
    assert weekday_offset(4, 3) == 6
    assert weekday_offset(5, 3) == 5
    assert weekday_offset(6, 3) == 4
    assert weekday_offset(7, 3) == 3