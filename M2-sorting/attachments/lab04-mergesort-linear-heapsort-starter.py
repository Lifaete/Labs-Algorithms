#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 4. MergeSort, Counting, Radix и HeapSort: оценка производительности — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-04 и правилами использования генеративного ИИ
(docs/ai-verification.md). QuickSort перенесите из собственной ЛР 3.

Запуск: python lab04-mergesort-linear-heapsort-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import time
import math
import os

import matplotlib
matplotlib.use("Agg")   # без GUI — надёжно при запуске из терминала
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. Сортировки (реализуются вручную; sorted() используется только как эталон)
# ---------------------------------------------------------------------------


def merge(left: list, right: list, key=lambda x: x) -> list:
    """Стабильное слияние двух отсортированных списков в новый список.
    Стабильность: при равенстве ключей элемент из left идёт раньше.
    Ожидаемая сложность: O(n log n)
    """
    res, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            res.append(left[i])
            i += 1
        else:
            res.append(right[j])
            j += 1
    res.extend(left[i:])
    res.extend(right[j:])
    return res


def merge_sort(a: list, key=lambda x: x) -> list:
    """MergeSort: возвращает новый отсортированный список.
    Ожидаемая сложность:  время O(n log n) во всех случаях, память O(n), стабилен.
    """
    if len(a) <= 1:
        return list(a)
    mid = len(a) // 2
    return merge(merge_sort(a[:mid], key), merge_sort(a[mid:], key), key)


def counting_sort(a: list[int], key_max: int) -> list[int]:
    """Устойчивая сортировка подсчётом: ключи — целые из диапазона [0, key_max].
    Схема: массив счётчиков -> префиксные суммы -> расстановка с конца.
    Ожидаемые время и память: O(n + k), k = key_max + 1. Стабильна.
    """
    k = key_max + 1
    counts = [0] * k
    for x in a:
        counts[x] += 1
    for i in range(1, k):
        counts[i] += counts[i - 1]
    out = [0] * len(a)
    for i in range(len(a) - 1, -1, -1):
        x = a[i]
        counts[x] -= 1
        out[counts[x]] = x
    return out


def _counting_by_digit(a: list[int], exp: int) -> list[int]:
    """Устойчивая поразрядная сортировка по цифре (a[i]//exp)%10."""
    counts = [0] * 10
    for x in a:
        counts[(x // exp) % 10] += 1
    for i in range(1, 10):
        counts[i] += counts[i - 1]
    out = [0] * len(a)
    for i in range(len(a) - 1, -1, -1):
        d = (a[i] // exp) % 10
        counts[d] -= 1
        out[counts[d]] = a[i]
    return out


def radix_sort_lsd(a: list[int]) -> list[int]:
    """RadixSort LSD по десятичным разрядам, неотрицательные целые.
    Поверх устойчивой поразрядной counting-сортировки: от младшего разряда
    к старшему. Ожидаемая сложность: Время O(d·(n+10)), d — число десятичных разрядов.
    """
    if not a:
        return []
    cur = list(a)
    exp = 1
    m = max(cur)
    while m // exp > 0:
        cur = _counting_by_digit(cur, exp)
        exp *= 10
    return cur


def sift_down(a: list[int], i: int, n: int) -> None:
    """Просейка вниз элемента i в куче a[0:n] (max-heap), на месте."""
    while True:
        largest, l, r = i, 2*i+1, 2*i+2
        if l < n and a[l] > a[largest]:
            largest = l
        if r < n and a[r] > a[largest]:
            largest = r
        if largest == i:
            return
        a[i], a[largest] = a[largest], a[i]
        i = largest


def heap_sort(a: list[int]) -> None:
    """HeapSort in-place: сортирует список a на месте, без вспомогательного массива.
    Сложность: время O(n log n), память O(1), нестабилен.
    """
    n = len(a)
    for i in range(n//2-1, -1, -1): # построение кучи O(n)
        sift_down(a, i, n)
    for end in range(n-1, 0, -1): # извлечение максимумов
        a[0], a[end] = a[end], a[0]
        sift_down(a, 0, end)


def quick_sort(a: list, rng: random.Random | None = None) -> list:
    """QuickSort с рандомизацией опорного элемента — перенести из своей ЛР 3."""
    if rng is None:
        rng = random.Random()
    arr = a.copy()

    def _quick_sort(lo: int, hi: int) -> None:
        if lo >= hi:
            return
        pivot_idx = rng.randrange(lo, hi)
        pivot = arr[pivot_idx]  # Выбираем случайный опорный элемент
        # Разбиение
        i, j = lo, hi - 1
        while i <= j:
            while arr[i] < pivot:
                i += 1
            while arr[j] > pivot:
                j -= 1
            if i <= j:
                arr[i], arr[j] = arr[j], arr[i]
                i += 1
                j -= 1
        # Рекурсивно сортируем левую и правую части
        _quick_sort(lo, j + 1)
        _quick_sort(i, hi)

    _quick_sort(0, len(arr))
    return arr


# ---------------------------------------------------------------------------
# 2. Верификация: инварианты + сверка с эталоном sorted()
#    (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------


def self_check() -> None:
    """Граничные и типовые случаи, стабильность, сверка с эталоном sorted()."""
    # Граничные случаи: пустой массив, один элемент, все элементы равны
    assert merge_sort([]) == []
    assert merge_sort([7]) == [7]
    assert merge_sort([5, 5, 5]) == [5, 5, 5]
    assert counting_sort([], key_max=10) == []
    assert radix_sort_lsd([0]) == [0]
    single = [42]
    heap_sort(single)
    assert single == [42]

    # Стабильность слияния: пары (ключ, порядковый номер); эталон sorted() стабилен,
    # поэтому при равных ключах порядок номеров обязан совпасть
    rng = random.Random(0)
    pairs = [(rng.randint(0, 5), i) for i in range(100)]
    assert merge_sort(pairs, key=lambda p: p[0]) == sorted(pairs, key=lambda p: p[0])

    # Случайные тесты: инвариант перестановки + сверка с эталоном
    for _ in range(200):
        a = [rng.randint(0, 999) for _ in range(rng.randint(0, 60))]
        expected = sorted(a)
        assert merge_sort(a) == expected
        assert counting_sort(a, key_max=999) == expected
        assert radix_sort_lsd(a) == expected
        buf = list(a)
        heap_sort(buf)
        assert buf == expected
        assert sorted(buf) == expected  # выход — перестановка входа
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 2b. Log-log графики по каждому распределению (matplotlib)
# ---------------------------------------------------------------------------

# (имя, функция, маркер, стиль линии)
PLOT_ALGOS = [
    ("merge_sort",     lambda a: merge_sort(a),                              "o", "-"),
    ("counting_sort",  lambda a: counting_sort(a, key_max=max(a, default=0)), "s", "-"),
    ("radix_sort_lsd", lambda a: radix_sort_lsd(a),                          "^", "-"),
    ("heap_sort",      lambda a: heap_sort(a),                               "D", "-"),
    ("quick_sort",     lambda a: quick_sort(a),                              "v", "-"),
    ("sorted()",       lambda a: sorted(a),                                  "x", "--"),
]


def _fit_slope(pts: list[tuple[int, float]]) -> float:
    """Наклон прямой в log-log (показатель степени) для подписи легенды."""
    pts = [(n, t) for n, t in pts if t > 0]
    if len(pts) < 2:
        return float("nan")
    xs = [math.log(n) for n, _ in pts]
    ys = [math.log(t) for _, t in pts]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    return num / den if den else float("nan")


def build_plots(seed: int, out_dir: str = "plots") -> None:
    """Собирает медианные времена по всем n и строит отдельный log-log
    график на каждое распределение. Файлы: plots/bench_<dist>.png."""
    os.makedirs(out_dir, exist_ok=True)
    rng = random.Random(seed)

    # results[dist][algo] = [(n, t), ...]
    results: dict[str, dict[str, list[tuple[int, float]]]] = {}

    for n in SIZES:
        datasets = make_datasets(rng, n)
        for dist_name, data in datasets.items():
            bucket = results.setdefault(
                dist_name, {name: [] for name, *_ in PLOT_ALGOS}
            )
            for algo_name, fn, _marker, _linestyle in PLOT_ALGOS:
                # counting_sort на широком диапазоне k ~ 10^9 — вне применимости
                if algo_name == "counting_sort" and dist_name == "random_wide":
                    continue
                bucket[algo_name].append((n, bench(fn, data)))

    for dist_name, per_algo in results.items():
        fig, ax = plt.subplots(figsize=(8, 5.5))
        for algo_name, _fn, marker, linestyle in PLOT_ALGOS:
            pts = per_algo.get(algo_name, [])
            if not pts:
                continue
            xs = [n for n, _ in pts]
            ys = [t for _, t in pts]
            slope = _fit_slope(pts)
            ax.plot(
                xs, ys,
                marker=marker, linestyle=linestyle,
                linewidth=1.6, markersize=5,
                label=f"{algo_name} (наклон≈{slope:.2f})",
            )
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("n (размер массива, log)")
        ax.set_ylabel("t, с (медиана, log)")
        ax.set_title(f"Бенчмарк сортировок — распределение: {dist_name}")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=9)
        fig.tight_layout()
        path = os.path.join(out_dir, f"bench_{dist_name}.png")
        fig.savefig(path, dpi=150)
        plt.close(fig)
        print(f"  график сохранён: {path}")

# ---------------------------------------------------------------------------
# 3. Бенчмарк (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5
SMALL_KEY_MAX = 100        # узкий диапазон: counting уместен
WIDE_KEY_MAX = 10**9       # широкий диапазон: counting теряет смысл (обсудить в отчёте)


def make_datasets(rng: random.Random, n: int) -> dict[str, list[int]]:
    """Массивы разных распределений и диапазонов ключей для размера n."""
    almost = list(range(n))
    for _ in range(max(1, n // 100)):  # ~1 % случайных обменов
        i, j = rng.randrange(n), rng.randrange(n)
        almost[i], almost[j] = almost[j], almost[i]
    return {
        "random_wide": [rng.randint(0, WIDE_KEY_MAX) for _ in range(n)],
        "random_small": [rng.randint(0, SMALL_KEY_MAX) for _ in range(n)],
        "sorted": list(range(n)),
        "reversed": list(range(n, 0, -1)),
        "almost_sorted": almost,
    }


def bench(fn, data: list[int]) -> float:
    """Медиана времени fn на копии data по REPEATS запускам, с прогревом.

    Каждый запуск получает свежую копию: сортировка на месте не должна
    превращать последующие запуски в сортировку уже отсортированного массива.
    """
    fn(list(data))  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        buf = list(data)
        t0 = time.perf_counter()
        fn(buf)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int) -> None:
    rng = random.Random(seed)
    algorithms = [
        ("merge_sort", merge_sort),
        ("counting_sort", lambda a: counting_sort(a, key_max=max(a, default=0))),
        ("radix_sort_lsd", radix_sort_lsd),
        ("heap_sort", heap_sort),
        ("quick_sort (ЛР 3)", quick_sort),
        ("sorted() (эталон)", sorted),
    ]
    for n in SIZES:
        datasets = make_datasets(rng, n)
        print(f"\nn = {n}:")
        for dist_name, data in datasets.items():
            print(f"  распределение {dist_name}:")
            for algo_name, fn in algorithms:
                if algo_name == "counting_sort" and dist_name == "random_wide":
                    # счётчики размера ~10^9 не помещаются в память — граница
                    # применимости counting; зафиксировать в таблице свойств
                    print(f"    {algo_name:>18}: пропуск (диапазон ключей)")
                    continue
                print(f"    {algo_name:>18}: t = {bench(fn, data):.6f} c")
    print("\nСтроим log-log графики...")
    build_plots(seed)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    run_benchmarks(seed)


if __name__ == "__main__":
    main()
