from fastapi import APIRouter
from app.schemas import OrderField, Response
from app.counter import Counter


workpiece_router = APIRouter()


@workpiece_router.post("/order")
async def calculate_best_fit(order: OrderField):
    workpieces = order.input
    max_lenght = order.max_length
    counter = Counter()
    cuts = counter.count_best_fit(input=workpieces, max_length=max_lenght)
    return cuts


@workpiece_router.post("/greedy")
async def calculate_ffd(order: OrderField):
    workpieces = order.input
    max_length = order.max_length
    counter = Counter()
    cuts = counter.count_ffd(input=workpieces, max_length=max_length)
    return cuts


@workpiece_router.post("/gilgom")
async def calculate_gilgom(order: OrderField):
    counter = Counter()
    workpieces = order.input
    max_length = order.max_length
    response = counter.count_gilmore_gomori(input=workpieces, max_length=max_length)
    return response


@workpiece_router.post("/sravnit")
async def sravnenie_algoritmov(order: OrderField):
    workpieces = order.input
    max_length = order.max_length
    counter = Counter()
    best_fit_cuts = counter.count_best_fit(input=workpieces, max_length=max_length)
    ffd_cuts = counter.count_ffd(input=workpieces, max_length=max_length)
    return {
        "Потрачено хлыстов в супер алгоритме": len(best_fit_cuts),
        "Потрачено хлыстов в жадную": len(ffd_cuts)
    }
