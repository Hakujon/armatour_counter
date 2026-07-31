import pytest
from app.schemas import BaseWorkpiece, CuttedBar, ReadyPattern, Response
from app.algorythm import gilmore_gomori_cutting_stock

# 1. Functional tests (refactored/parameterized)
@pytest.mark.parametrize("demands, expected_whips", [
    ([(6000, 1)], 1),
    ([(11700, 1)], 1),
    ([(5000, 1), (6000, 1)], 1), # Both fit in one
    ([(6000, 2)], 2),           # Need 2
])
def test_cutting_scenarios(demands, expected_whips):
    result = gilmore_gomori_cutting_stock(demands, 11700)
    assert result.total_whips == expected_whips

def test_all_pieces_accounted():
    demands = [(5000, 5), (600, 17), (800, 3)]
    result = gilmore_gomori_cutting_stock(demands=demands, max_whip=11700)
    demands_dict = {length: quantity for length, quantity in demands}
    result_dict = {}
    for pattern in result.patterns:
        for workpiece in pattern.cutted_bar.workpieces:
            if workpiece.length in result_dict:
                result_dict[workpiece.length] += pattern.count
            else:
                result_dict[workpiece.length] = pattern.count

    for length, quantity in demands:
        assert result_dict.get(length, 0) >= quantity


# 2. Validation tests (Expected to fail)
@pytest.mark.parametrize("invalid_length", [1, 25, 49])
def test_workpiece_too_small(invalid_length):
    with pytest.raises(ValueError, match="Длина заготовки должна быть не менее 50 мм"):
        gilmore_gomori_cutting_stock([(invalid_length, 1)], 11700)

def test_empty_input():
    with pytest.raises((ValueError, AssertionError)):
        gilmore_gomori_cutting_stock([], 11700)

def test_workpiece_exceeds_max_whip():
    max_whip = 11700
    with pytest.raises(ValueError, match="превышает длину хлыста"):
        gilmore_gomori_cutting_stock([(max_whip + 1, 1)], max_whip)

def test_negative_workpiece():
    with pytest.raises((ValueError, AssertionError)):
        gilmore_gomori_cutting_stock([(1200, 2), (-700, 4)], 11700)

# 3. Correctness tests
def test_pattern_sum_is_valid():
    demands = [(5000, 5), (600, 17), (800, 3)]
    result = gilmore_gomori_cutting_stock(demands, 11700)
    for pattern in result.patterns:
        total_length = sum(wp.length for wp in pattern.cutted_bar.workpieces)
        assert total_length <= 11700

def test_minimization_simple():
    # [(6000, 2)], max_whip 11700 -> needs 2 whips
    result = gilmore_gomori_cutting_stock([(6000, 2)], 11700)
    assert result.total_whips == 2
