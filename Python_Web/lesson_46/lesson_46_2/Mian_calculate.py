import os
import time
import math
from concurrent.futures import ProcessPoolExecutor

from fastapi import FastAPI, HTTPException

import compute
from schemas import CalculateRequest, CalculateResponse

app = FastAPI(title="Math Calculator API")

MAX_FACTORIAL_N = 1000
MAX_PRIME_RANGE = 2_000_000       # range_end - range_start
MAX_MATRIX_SIZE = 200
MAX_ARRAY_SIZE = 5_000_000

N_WORKERS = max(2, os.cpu_count() or 2)

process_pool: ProcessPoolExecutor | None = None


@app.on_event("startup")
def startup_event():
    global process_pool
    process_pool = ProcessPoolExecutor(max_workers=N_WORKERS)


@app.on_event("shutdown")
def shutdown_event():
    if process_pool is not None:
        process_pool.shutdown(wait=True)


@app.post("/calculate", response_model=CalculateResponse)
def calculate(request: CalculateRequest):
    start_time = time.perf_counter()

    if request.operation == "factorial":
        result = _handle_factorial(request.n)

    elif request.operation == "primes":
        result = _handle_primes(request.range_start, request.range_end)

    elif request.operation == "matrix_multiply":
        result = _handle_matrix_multiply(request.matrix_size)

    elif request.operation == "array_stats":
        result = _handle_array_stats(request.array_size, request.data)

    else:
        raise HTTPException(status_code=400, detail=f"Невідома операція: {request.operation}")

    elapsed = time.perf_counter() - start_time
    return CalculateResponse(
        operation=request.operation,
        execution_time_seconds=round(elapsed, 4),
        result=result,
    )



def _handle_factorial(n: int) -> dict:
    if n < 0 or n > MAX_FACTORIAL_N:
        raise HTTPException(
            status_code=400,
            detail=f"n має бути в межах [0, {MAX_FACTORIAL_N}].",
        )

    n_chunks = min(N_WORKERS, max(1, n // 50))
    chunks = compute.compute_factorial_chunks(n, n_chunks)

    futures = [process_pool.submit(compute._range_product, c[0], c[1]) for c in chunks]
    partials = [f.result() for f in futures]
    value = compute.combine_factorial_results(partials)

    return {
        "n": n,
        "factorial": str(value),
        "digits": len(str(value)),
        "workers_used": len(chunks),
    }


def _handle_primes(range_start: int, range_end: int) -> dict:
    if range_start < 0 or range_end < range_start:
        raise HTTPException(status_code=400, detail="Некоректний діапазон: range_end має бути >= range_start >= 0.")
    if range_end - range_start > MAX_PRIME_RANGE:
        raise HTTPException(
            status_code=400,
            detail=f"Діапазон завеликий. Максимум {MAX_PRIME_RANGE} чисел за один запит.",
        )

    base_primes = compute._simple_sieve(int(math.isqrt(range_end)) + 1)

    n_workers = N_WORKERS
    span = range_end - range_start + 1
    step = max(1, span // n_workers + 1)

    segments = []
    s = range_start
    while s <= range_end:
        e = min(s + step - 1, range_end)
        segments.append((s, e))
        s = e + 1

    futures = [
        process_pool.submit(compute.find_primes_in_segment, seg[0], seg[1], base_primes)
        for seg in segments
    ]
    primes = []
    for f in futures:
        primes.extend(f.result())
    primes.sort()

    return {
        "range_start": range_start,
        "range_end": range_end,
        "count": len(primes),
        "primes": primes,
        "workers_used": len(segments),
    }


def _handle_matrix_multiply(n: int) -> dict:
    if n < 1 or n > MAX_MATRIX_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"matrix_size має бути в межах [1, {MAX_MATRIX_SIZE}].",
        )

    matrix_a = compute.generate_random_matrix(n)
    matrix_b = compute.generate_random_matrix(n)

    n_workers = min(N_WORKERS, n)
    chunk_size = max(1, n // n_workers)
    row_chunks = [matrix_a[i:i + chunk_size] for i in range(0, n, chunk_size)]

    futures = [process_pool.submit(compute.multiply_row_chunk, chunk, matrix_b) for chunk in row_chunks]
    result_matrix = []
    for f in futures:
        result_matrix.extend(f.result())

    return {
        "matrix_size": n,
        "workers_used": len(row_chunks),
        "result_preview": [row[:5] for row in result_matrix[:5]],
        "full_result_shape": [n, n],
    }


def _handle_array_stats(array_size: int | None, data: list[float] | None) -> dict:
    if data is not None:
        if len(data) > MAX_ARRAY_SIZE:
            raise HTTPException(status_code=400, detail=f"Масив завеликий. Максимум {MAX_ARRAY_SIZE} елементів.")
        array = data
    else:
        if array_size < 1 or array_size > MAX_ARRAY_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"array_size має бути в межах [1, {MAX_ARRAY_SIZE}].",
            )
        array = compute.generate_random_array(array_size)

    n_workers = N_WORKERS
    size = len(array)
    chunk_size = max(1, size // n_workers)
    chunks = [array[i:i + chunk_size] for i in range(0, size, chunk_size)]

    futures = [process_pool.submit(compute.partial_sum_stats, chunk) for chunk in chunks]
    partials = [f.result() for f in futures]

    sorted_array = sorted(array)
    stats = compute.combine_array_stats(partials, sorted_array)

    return {
        "array_size": size,
        "workers_used": len(chunks),
        **stats,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8007)