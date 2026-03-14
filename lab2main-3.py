import random


def tree_sort(arr):
    if len(arr) <= 1:
        return arr

    root = arr[0]

    left = []
    for x in arr[1:]:
        if x < root:
            left.append(x)

    right = []
    for x in arr[1:]:
        if x >= root:
            right.append(x)

    return tree_sort(left) + [root] + tree_sort(right)


while True:
    print("\n1 - Ручной ввод")
    print("2 - Ввод файлом")
    print("3 - Генерация массива")
    print("4 - Выход")
    choice = input("Выберите: ")

    if choice == "1":
        numbers = list(map(int, input("Числа: ").split()))
    elif choice == "2":
        filename = input("Путь: ").strip('"')
        with open(filename, 'r') as f:
            numbers = list(map(int, f.read().split()))
    elif choice == "3":
        n = int(input("Размер: "))
        numbers = [random.randint(1, 100) for _ in range(n)]
    elif choice == "4":
        break
    else:
        print("Неверный выбор")
        continue

    print("До:", numbers)
    print("После:", tree_sort(numbers))

    if input("Сохранить? (y/n): ") == "y":
        filename = input("Имя файла формата 'KadyrovStatement.txt': ").strip('"')
        with open(filename, 'w') as f:
            f.write(" ".join(map(str, tree_sort(numbers))))