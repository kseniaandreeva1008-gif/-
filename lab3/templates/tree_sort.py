"""
МОДУЛЬ СОРТИРОВКИ ДЕРЕВОМ (Tree Sort)
"""


def tree_sort(arr):
    """
    Сортировка деревом (рекурсивная версия)
    """
    # Проверка на корректность входных данных
    if not isinstance(arr, list):
        raise TypeError("Входные данные должны быть списком")

    if arr and not all(isinstance(x, (int, float)) for x in arr):
        raise TypeError("Все элементы списка должны быть числами")

    # Базовый случай
    if len(arr) <= 1:
        return arr

    # Первый элемент - корень
    root = arr[0]

    # Левый подмассив (меньше корня)
    left = [x for x in arr[1:] if x < root]

    # Правый подмассив (больше или равно корню)
    right = [x for x in arr[1:] if x >= root]

    # Рекурсивная сортировка и объединение
    return tree_sort(left) + [root] + tree_sort(right)


# Проверка работы модуля
if __name__ == "__main__":
    test_array = [64, 25, 12, 22, 11]
    print("Исходный массив:", test_array)
    sorted_array = tree_sort(test_array)
    print("Отсортированный массив:", sorted_array)