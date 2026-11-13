import random

def quicksort(data: list[int]) -> list[int]:
    """Трёхпутевой quicksort. Средняя сложность O(n log n), O(n) на равных.
    Худший случай O(n^2) теоретически возможен, но на монотонных входах
    не деградирует благодаря случайному выбору опорного элемента."""
    arr = list(data)
    _qs(arr, 0, len(arr) - 1, random.Random(0))
    return arr

def _qs(a, lo, hi, rnd):
    while lo < hi:
        p = rnd.randint(lo, hi) # случайный опорный — защита от монотонных входов
        a[lo], a[p] = a[p], a[lo]
        pivot = a[lo]
        lt, i, gt = lo, lo, hi
        while i <= gt: # трёхпутевое разбиение: < , == , >
            if a[i] < pivot:
                a[lt], a[i] = a[i], a[lt]; lt += 1; i += 1
            elif a[i] > pivot:
                a[i], a[gt] = a[gt], a[i]; gt -= 1
            else:
                i += 1
        if lt - lo < hi - gt: # рекурсия в меньшую часть — глубина O(log n)
            _qs(a, lo, lt - 1, rnd); lo = gt + 1
        else:
            _qs(a, gt + 1, hi, rnd); hi = lt - 1

