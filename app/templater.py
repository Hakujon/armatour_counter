from app.schemas import InputField, GroupWorkpieces


def make_pieces_from_input(order: InputField) -> list[int]:
    pieces: list[tuple[int, int]]= []
    for group in order.workpieces:
        pieces.append((group.length, group.quantity))

    workpieces = [value for value, count in pieces for _ in range(count)]
    return workpieces


def make_demands_from_input(order: InputField) -> list[tuple[int, int]]:
    pieces = [(group.length, group.quantity) for group in order.workpieces]
    return pieces

def create_cool_view(bars: list, max_length: int):
    answer = ""
    for i, bar in enumerate(bars, 1):
        left_length = max_length - sum(bar)
        # print(f"Текущий срез №{i}: {bar}, остаток: {left_length}")
        answer += f"Текущий срез №{i}: {bar}, остаток: {left_length} \n"
    return answer

if __name__ == "__main__":
    order = InputField(workpieces=
        [GroupWorkpieces(length=500, quantity=5),
         GroupWorkpieces(length=300, quantity=2)]
    )
    print(make_pieces_from_input(order=order))