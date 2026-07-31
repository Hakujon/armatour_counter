from app.schemas import InputField, CuttedBar, BaseWorkpiece, Response
from app.templater import make_pieces_from_input, make_demands_from_input
from app.algorythm import gilmore_gomori_cutting_stock


def find_best_fit(pieces: list[int], max_length: int) -> list:
    bars: list[CuttedBar] = []

    for piece in pieces:
        found = False
        best_bar = CuttedBar(left_length=max_length)
        minimal_left_length = float("inf")
        for bar in bars:
            left_length = bar.left_length - piece
            if left_length >= 0:
                if left_length < minimal_left_length:
                    best_bar = bar
                    minimal_left_length = left_length
                    found = True

        best_bar.workpieces.append(BaseWorkpiece(length=piece))
        best_bar.used_length += piece
        best_bar.left_length -= piece
        if not found:
            bars.append(best_bar)
    return bars


def findfirstdecrease(pieces: list[int], max_length: int) -> list:
    bars: list[CuttedBar] = []
    for piece in pieces:
        found = False
        best_bar = CuttedBar(left_length=max_length)
        for bar in bars:
            left_length = bar.left_length - piece
            if left_length >= 0:
                found = True
                best_bar = bar

        best_bar.workpieces.append(BaseWorkpiece(length=piece))
        best_bar.used_length += piece
        best_bar.left_length -= piece
        if not found:
            bars.append(best_bar)
    return bars




class Counter:
    def count_best_fit(self, input: InputField, max_length: int) -> list:
        pieces = make_pieces_from_input(order=input)
        best_fit_bars = find_best_fit(pieces=pieces, max_length=max_length)
        return best_fit_bars

    def count_ffd(self, input: InputField, max_length: int) -> list:
        pieces = make_pieces_from_input(order=input)
        ffd_bars = findfirstdecrease(pieces=pieces, max_length=max_length)
        return ffd_bars

    def count_gilmore_gomori(self, input:InputField, max_length: int) -> Response:
        demands = make_demands_from_input(order=input)
        response = gilmore_gomori_cutting_stock(demands=demands, max_whip=max_length)
        return response
