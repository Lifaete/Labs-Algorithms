#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 3. Простые сортировки и QuickSort с рандомизацией — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-03 и правилами использования генеративного ИИ
(docs/ai-verification.md).

Запуск: python lab03-simple-sorts-quicksort-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import time


# ---------------------------------------------------------------------------
# 1. Простые сортировки со счётчиками (сортируют КОПИЮ входа, вход не меняют)
#    Каждая функция возвращает кортеж: (отсортированный список,
#    число сравнений ключей, число обменов/перемещений элементов).
# ---------------------------------------------------------------------------


def bubble_sort(a: list) -> tuple[list, int, int]:
    """Сортировка пузырьком. Ожидаемая сложность: O(n^2) в среднем/худшем; O(n) в лучшем (упорядоченный вход)."""
    switches = 0
    compares = 0
    for i in range(len(a) - 1):
        swapped = False
        for j in range(len(a) - 1):
            if a[j] > a[j + 1]:
                compares += 1
                a[j], a[j + 1] = a[j + 1], a[j]
                switches += 1
                swapped = True
        if not swapped:
            break
    return a, compares, switches


def insertion_sort(a: list) -> tuple[list, int, int]:
    """Сортировка вставками. Ожидаемая сложность: Лучший случай O(n) (упорядочен), худший O(n^2) (обратный)."""
    compares = 0
    moves = 0
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0:
            compares += 1
            if a[j] > key:
                a[j + 1] = a[j]
                moves += 1
                j -= 1
            else:
                break
        a[j + 1] = key
        if j + 1 != i:
            moves += 1
    return a, compares, moves


def selection_sort(a: list) -> tuple[list, int, int]:
    """Сортировка выбором. Ожидаемая сложность: Θ(n^2) сравнений всегда; обменов ≤ n-1. Не зависит от входа."""
    compares = 0
    switches = 0
    for i in range(len(a) - 1):
        m = i
        for j in range(i + 1, len(a)):
            compares += 1
            if a[j] < a[m]:
                m = j
        if m != i:
            a[i], a[m] = a[m], a[i]
            switches += 1
    return a, compares, switches


# ---------------------------------------------------------------------------
# 2. QuickSort с рандомизированным опорным элементом
# ---------------------------------------------------------------------------


def quick_sort(a: list, rng: random.Random | None = None) -> list:
    """Ожидаемая сложность: В среднем O(n log n); худший O(n^2) маловероятен из-за рандомизации."""
    if rng is None:
        rng = random.Random()
    arr = a.copy()
    def _quick_sort(lo: int, hi: int) -> None:
        if lo >= hi:
            return
        pivot_idx = rng.randrange(lo, hi)
        pivot = arr[pivot_idx] # Выбираем случайный опорный элемент
        # Разбиение
        i, j = lo, hi - 1
        while i <= j:
            while arr[i] < pivot:
                i += 1
            while arr[j] > pivot:
                j -= 1
            if i <= j:
                arr[i], arr[j] = arr [j], arr[i]
                i += 1
                j -= 1
        # Рекурсивно сортируем левую и правую части
        _quick_sort(lo, j + 1)
        _quick_sort(i, hi)

    _quick_sort(0, len(arr))
    return arr




# ---------------------------------------------------------------------------
# 3. Демонстрация стабильности на парах (ключ, метка)
# ---------------------------------------------------------------------------


def stability_demo() -> None:
    """Показать, какие из четырёх сортировок стабильны.

    План: взять массив пар (ключ, метка) с повторяющимися ключами, например
    [(2, "a"), (1, "b"), (2, "c"), (1, "d")], отсортировать каждой сортировкой
    по ключу (сравнение только по p[0]!) и напечатать порядок меток при равных
    ключах. Вывод о стабильности каждой сортировки включить в отчёт.
    """
    data = [(2, "a"), (1, "b"), (2, "c"), (1, "d"), (2, "e")]
    print("\nДемонстрация стабильности:")
    print(f"Исходный: {data}")

    res, _, _ = bubble_sort(data)
    print(f"bubble_sort: {res}")

    res, _, _ = insertion_sort(data)
    print(f"insertion_sort^ {res}")

    res, _, _ = selection_sort(data)
    print(f"selection_sort^ {res}")

    res, _, _ = quick_sort(data)
    print(f"quick_sort: {res}")

    print("\nВывод: bubble_sort и insertion_sort - стабильные,")
    print("selection_sort и quick_sort - нестабильные")


# ---------------------------------------------------------------------------
# 4. Классы входов (данные по варианту, детерминированно по seed)
# ---------------------------------------------------------------------------


def make_inputs(n: int, seed: int) -> dict[str, list[int]]:
    """Три класса входов размера n: упорядоченный, случайный, обратный."""
    rng = random.Random(seed + n)  # свой поток для каждого размера
    data = [rng.randint(-1_000_000, 1_000_000) for _ in range(n)]
    return {
        "упорядоченный": sorted(data),
        "случайный": data,
        "обратный": sorted(data, reverse=True),
    }


# ---------------------------------------------------------------------------
# 5. Верификация (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------

ALGORITHMS = {
    "bubble_sort": lambda a: bubble_sort(a)[0],
    "insertion_sort": lambda a: insertion_sort(a)[0],
    "selection_sort": lambda a: selection_sort(a)[0],
    "quick_sort": lambda a: quick_sort(a, random.Random(0)),
}


def is_sorted(a: list) -> bool:
    """Инвариант 1: неубывающий порядок элементов."""
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))


def self_check() -> None:
    """Граничные случаи, инварианты сортировки и сверка с эталоном sorted()."""
    boundary = [
        [],                    # пустой массив
        [7],                   # один элемент
        [5, 5, 5, 5],          # все элементы равны
        [1, 2, 3, 4, 5],       # уже отсортирован
        [5, 4, 3, 2, 1],       # обратный порядок
    ]
    for name, fn in ALGORITHMS.items():
        for a in boundary:
            res = fn(list(a))
            assert is_sorted(res), f"{name}: нарушен порядок на {a}"
            assert sorted(res) == sorted(a), f"{name}: не перестановка входа {a}"

    # Сверка с эталоном из стандартной библиотеки на сотнях случайных входов.
    rng = random.Random(0)
    for _ in range(300):
        a = [rng.randint(-100, 100) for _ in range(rng.randint(0, 80))]
        expected = sorted(a)
        for name, fn in ALGORITHMS.items():
            assert fn(list(a)) == expected, f"{name}: расходится с sorted() на {a}"

    # Счётчики: у сортировки выбором ровно n*(n-1)/2 сравнений на любом входе.
    _, comparisons, _ = selection_sort([3, 1, 2, 5, 4])
    assert comparisons == 10, "selection_sort: неверный счётчик сравнений"
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 6. Бенчмарк (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES_QUADRATIC = [500, 1_000, 2_000, 4_000, 8_000]     # для простых сортировок
SIZES_QUICK = [1_000, 3_000, 10_000, 30_000, 100_000]   # для QuickSort
REPEATS = 5


def bench(fn, data: list) -> float:
    """Медиана времени выполнения fn(копия data) по REPEATS запускам, с прогревом."""
    fn(list(data))  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        arg = list(data)  # свежая копия: сортировка не должна получать свой результат
        t0 = time.perf_counter()
        fn(arg)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int) -> None:
    """Замеры всех алгоритмов на трёх классах входов; результат — таблица в stdout."""
    plans = [
        ("bubble_sort", ALGORITHMS["bubble_sort"], SIZES_QUADRATIC),
        ("insertion_sort", ALGORITHMS["insertion_sort"], SIZES_QUADRATIC),
        ("selection_sort", ALGORITHMS["selection_sort"], SIZES_QUADRATIC),
        ("quick_sort", lambda a: quick_sort(a, random.Random(seed)), SIZES_QUICK),
    ]
    for name, fn, sizes in plans:
        print(f"\n{name}:")
        for n in sizes:
            for cls, data in make_inputs(n, seed).items():
                print(f"  n={n:>7}  вход={cls:<13} t={bench(fn, data):.6f} c")

    import math
    import matplotlib
    matplotlib.use("Agg")  # без интерактивного окна — сохраняем в файл
    import matplotlib.pyplot as plt

    classes = ("упорядоченный", "случайный", "обратный")
    # ---------- 1. Таблица времени ----------
    print("\n===== ВРЕМЯ ВЫПОЛНЕНИЯ (медиана из 5 повторов) =====")
    times: dict[str, dict[str, dict[int, float]]] = {}
    for name, fn, sizes in plans:
        times[name] = {cls: {} for cls in classes}
        print(f"\n{name}:")
        for n in sizes:
            for cls, data in make_inputs(n, seed).items():
                t = bench(fn, data)
                times[name][cls][n] = t
                print(f"  n={n:>7}  вход={cls:<13} t={t:.6f} c")

    # ---------- 2. Таблица счётчиков для простых сортировок ----------
    print("\n===== СЧЁТЧИКИ (сравнения / обмены-перемещения) =====")
    counters = [
        ("bubble_sort", bubble_sort, SIZES_QUADRATIC),
        ("insertion_sort", insertion_sort, SIZES_QUADRATIC),
        ("selection_sort", selection_sort, SIZES_QUADRATIC),
    ]
    for name, fn, sizes in counters:
        print(f"\n{name}:")
        for n in sizes:
            for cls, data in make_inputs(n, seed).items():
                _, cmp_cnt, ops_cnt = fn(list(data))
                print(f"  n={n:>7}  вход={cls:<13} cmp={cmp_cnt:<10} ops={ops_cnt}")

    # ---------- 3. Log-log график 2x2 ----------
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    axes = axes.ravel()
    for ax, (name, _fn, sizes) in zip(axes, plans):
        for cls in classes:
            xs = sorted(times[name][cls].keys())
            ys = [times[name][cls][n] for n in xs]
            ax.plot(xs, ys, marker="o", label=cls)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("n (log)")
        ax.set_ylabel("время, с (log)")
        ax.set_title(name)
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()
    fig.suptitle(f"Log-log: время от размера входа (seed={seed})", fontsize=13)
    fig.tight_layout()
    fig.savefig("loglog.png", dpi=150)
    print("\nГрафик сохранён: loglog.png")

    # ---------- 4. Наклоны log-log ----------
    print("\n===== НАКЛОНЫ log-log (k ≈ Δlog t / Δlog n) =====")
    print(f"{'алгоритм':<16} {'класс входа':<16} {'наклон':>8}")
    for name, _fn, sizes in plans:
        for cls in classes:
            xs = sorted(times[name][cls].keys())
            ys = [times[name][cls][n] for n in xs]
            if len(xs) >= 2 and all(y > 0 for y in ys):
                k = (math.log(ys[-1]) - math.log(ys[0])) / (
                        math.log(xs[-1]) - math.log(xs[0])
                )
                print(f"{name:<16} {cls:<16} {k:>8.3f}")
            else:
                print(f"{name:<16} {cls:<16} {'—':>8}")

    print(
        "\nОриентиры: O(n²) → наклон ≈ 2; "
        "O(n log n) → ≈ 1.1–1.2; O(n) → ≈ 1."
    )

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    stability_demo()
    run_benchmarks(seed)


if __name__ == "__main__":
    main()
