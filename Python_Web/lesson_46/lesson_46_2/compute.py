import math
import random
from functools import reduce



def _range_product(start: int, end: int) -> int:
    result = 1
    for i in range(start, end + 1):
        result *= i
    return result


def compute_factorial_chunks(n: int, n_chunks: int) -> list[tuple[int, int]]:
    if n <= 1:
        return [(1, max(n, 1))]

    chunk_size = max(1, n // n_chunks)
    chunks = []
    start = 1
    while start <= n:
        end = min(start + chunk_size - 1, n)
        chunks.append((start, end))
        start = end + 1
    return chunks


def combine_factorial_results(partial_products: list[int]) -> int:
    return reduce(lambda a, b: a * b, partial_products, 1)



def _simple_sieve(limit: int) -> list[int]:
    if limit < 2:
        return []
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    return [i for i, val in enumerate(is_prime) if val]


def find_primes_in_segment(segment_start: int, segment_end: int, base_primes: list[int]) -> list[int]:
    segment_start = max(segment_start, 2)
    if segment_start > segment_end:
        return []

    size = segment_end - segment_start + 1
    is_prime = [True] * size

    for p in base_primes:
        if p * p > segment_end:
            break
        start_multiple = max(p * p, ((segment_start + p - 1) // p) * p)
        for multiple in range(start_multiple, segment_end + 1, p):
            is_prime[multiple - segment_start] = False

    return [segment_start + i for i, val in enumerate(is_prime) if val]



def generate_random_matrix(n: int, seed: int | None = None) -> list[list[float]]:
    rng = random.Random(seed)
    return [[rng.uniform(-10, 10) for _ in range(n)] for _ in range(n)]


def multiply_row_chunk(a_rows: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    n = len(b)
    result = []
    for row in a_rows:
        new_row = [
            sum(row[k] * b[k][j] for k in range(n))
            for j in range(n)
        ]
        result.append(new_row)
    return result



def generate_random_array(size: int, seed: int | None = None) -> list[float]:
    rng = random.Random(seed)
    return [rng.gauss(0, 1) for _ in range(size)]


def partial_sum_stats(chunk: list[float]) -> tuple[float, float, int]:
    total = sum(chunk)
    total_sq = sum(x * x for x in chunk)
    return total, total_sq, len(chunk)


def combine_array_stats(partials: list[tuple[float, float, int]], full_sorted_for_median: list[float]) -> dict:
    total_sum = sum(p[0] for p in partials)
    total_sq = sum(p[1] for p in partials)
    n = sum(p[2] for p in partials)

    mean = total_sum / n
    variance = (total_sq / n) - (mean ** 2)
    std_dev = math.sqrt(max(variance, 0))

    m = len(full_sorted_for_median)
    if m % 2 == 1:
        median = full_sorted_for_median[m // 2]
    else:
        median = (full_sorted_for_median[m // 2 - 1] + full_sorted_for_median[m // 2]) / 2

    return {
        "mean": mean,
        "median": median,
        "std_dev": std_dev,
        "count": n,
    }