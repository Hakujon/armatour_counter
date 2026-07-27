from ortools.linear_solver import pywraplp
from ortools.linear_solver.pywraplp import Solver
from ortools.sat.python import cp_model
from app.schemas import CuttedBar, BaseWorkpiece, ReadyPattern, Response
from pprint import pprint


def _solve_subproblem(shadow_prices: list, lengths: list, max_whip: int):
    model = cp_model.CpModel()
    num_items = len(lengths)

    pattern = [model.new_int_var(
        0, max_whip // lengths[whip], f'pattern_{whip}'
        ) for whip in range(num_items)]

    model.add(sum(pattern[whip] * lengths[whip] for whip in range(num_items)) <= max_whip)

    micro_bonus: list[int] = [int(lengths[i] * 0.01) for i in range(num_items)] # Бонус: 1 копейка за каждый мм длины

    model.maximize(
        sum((int(shadow_prices[i] * 10000) + micro_bonus[i]) * pattern[i] for i in range(num_items))
    )

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 1.0
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        new_pattern = [solver.Value(pattern[whip]) for whip in range(num_items)]

        obj_value = sum(shadow_prices[whip] * new_pattern[whip] for whip in range(num_items))
        return new_pattern, obj_value
    return None, 0


def _run_cutting_stock_optimization(demands: list[tuple[int, int]], max_whip: int):

    lengths = [detail[0] for detail in demands]
    quantities = [detail[1] for detail in demands]
    num_items = len(lengths)
    patterns = []
    for i in range(num_items):
        base_pattern = [0] * num_items
        base_pattern[i] = max_whip // lengths[i]
        patterns.append(base_pattern)

    print(f"Стартовое количество базовых шаблонов: {num_items}")
    MAX_ITERATIONS = 200
    iteration = 0
    while True:

        iteration += 1
        print(f"Попытка номер: {iteration}")
        if iteration >= MAX_ITERATIONS:
            print("Достигнут лимит итераций")
            break
        master_solver: Solver = pywraplp.Solver.CreateSolver("GLOP")
        master_solver.set_time_limit(8000)

        num_patterns = len(patterns)
        p_vars = [master_solver.NumVar(
            0, master_solver.infinity(), f'p_{pattern}'
            ) for pattern in range(num_patterns)]
        constraints = []
        for i in range(num_items):
            constraints.append(
                master_solver.Add(sum(patterns[j][i] * p_vars[j] for j in range(num_patterns)) >= quantities[i])
            )
        master_solver.Minimize(sum(p_vars[j] for j in range(num_patterns)))
        master_solver.Solve()

        shadow_prices = [constraints[i].dual_value() for i in range(num_items)]

        new_pattern, pattern_worth = _solve_subproblem(
            shadow_prices=shadow_prices,
            lengths=lengths,
            max_whip=max_whip)
        if new_pattern in patterns:
            print(f"Алгоритм начал повторяться на {iteration}-й итерации. Выходим.")
            break

        if pattern_worth <= 1.001:
            print(f"Цикл завершен на итерации номер {iteration}. Шаблонов лучше нет")
            break
        patterns.append(new_pattern)

    final_solver: Solver = pywraplp.Solver.CreateSolver("SCIP")
    num_patterns = len(patterns)
    pattern_int_vars = [final_solver.IntVar(0, final_solver.infinity(), f"p_int_{j}") for j in range(num_patterns)]

    for i in range(num_items):
        final_solver.Add(sum(patterns[j][i] * pattern_int_vars[j] for j in range(num_patterns)) >= quantities[i])

    final_solver.Minimize(sum(pattern_int_vars[j] for j in range(num_patterns)))

    final_solver.Solve()

    total_whips = 0
    ready_patterns: list[ReadyPattern] = []
    for j in range(num_patterns):
        count = int(pattern_int_vars[j].solution_value() + 0.5)
        if count > 0:
            total_whips += count
            parts_in_pattern = []
            workpieces = []
            for i in range(num_items):
                if patterns[j][i] > 0:
                    parts_in_pattern.extend([lengths[i]] * patterns[j][i])
                    for _ in range(patterns[j][i]):
                        workpieces.append(BaseWorkpiece(length=lengths[i]))
            used_length = sum(parts_in_pattern)
            waste = max_whip - used_length
            ready_patterns.append(ReadyPattern(cutted_bar=CuttedBar(left_length=waste, used_length=used_length,
                                            workpieces=workpieces), count=count))

    pprint(ready_patterns, compact=True)
    return Response(patterns=ready_patterns, total_whips=total_whips)


def gilmore_gomori_cutting_stock(demands: list[tuple[int, int]], max_whip: int):
    if not demands:
        raise ValueError("Demands list cannot be empty")

    for length, quantity in demands:
        if length <= 0 or quantity <= 0:
            raise ValueError("Length and quantity must be positive")
        if length < 50:
            raise ValueError("Длина заготовки должна быть не менее 50 мм")
        if length > max_whip:
            raise ValueError(f"Длина заготовки ({length} мм) превышает длину хлыста ({max_whip} мм)")

    return _run_cutting_stock_optimization(demands, max_whip)


if __name__ == "__main__":
    demands = [(6360, 39), (6740, 17), (6190, 9), (5070, 42), (1700, 16), (6830, 28),
 (7760, 23), (8190, 7), (620, 38), (8830, 44), (3320, 4), (5390, 40), (1470, 9),
 (590, 15), (6520, 2), (7580, 9), (840, 5), (1780, 8), (5280, 39), (1000, 23),
 (7210, 3), (2070, 22), (1650, 46), (4390, 3), (5210, 20), (4730, 25),
 (2190, 46), (2060, 5), (8600, 28), (5450, 11), (3410, 14), (2250, 22),
 (1190, 5), (6330, 15), (6880, 19), (8160, 35), (6040, 28), (5440, 13),
 (5560, 21), (5760, 36), (8520, 1), (8950, 39), (7550, 16), (6090, 37),
 (890, 15), (930, 28), (3670, 14), (2990, 15), (6780, 25), (8060, 38)]

    MAX_WHIP = 11700
    gilmore_gomori_cutting_stock(demands=demands, max_whip=MAX_WHIP)
