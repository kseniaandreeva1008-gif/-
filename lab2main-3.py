import random
import os
from datetime import datetime

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
    sorted_numbers = tree_sort(numbers)
    print("После:", sorted_numbers)

    # === СОХРАНЕНИЕ В ФАЙЛ (ИСХОДНЫЙ + ОТСОРТИРОВАННЫЙ) ===
    if input("Сохранить? (y/n): ") == "y":
        # Вводим путь к папке
        folder_path = input("Введите путь к папке (например, /Users/пользователь/Desktop/Моя папка): ").strip()
        
        # Убираем кавычки если есть
        folder_path = folder_path.replace('"', '').replace("'", "")
        
        # Проверяем, существует ли папка
        if not os.path.exists(folder_path):
            print(f"Ошибка: Папка '{folder_path}' не существует!")
            print("Создайте папку сначала или проверьте путь")
            continue
        
        # Вводим имя файла
        filename = input("Имя файла (например, result.txt): ").strip()
        if filename == "":
            filename = "sorted_result.txt"
        
        # Склеиваем путь
        full_path = os.path.join(folder_path, filename)
        
        # Получаем текущее время
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Сохраняем
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write("=" * 50 + "\n")
                f.write(f"РЕЗУЛЬТАТ СОРТИРОВКИ МЕТОДОМ ДЕРЕВА (TREE SORT)\n")
                f.write(f"Дата и время: {now}\n")
                f.write("=" * 50 + "\n\n")
                
                f.write(f"Исходный массив ({len(numbers)} элементов):\n")
                f.write(" ".join(map(str, numbers)))
                f.write("\n\n")
                
                f.write(f"Отсортированный массив ({len(sorted_numbers)} элементов):\n")
                f.write(" ".join(map(str, sorted_numbers)))
                f.write("\n\n")
                f.write("=" * 50 + "\n")
            
            print(f"Файл успешно сохранен: {full_path}")
            print(f"   - Исходный массив: {numbers}")
            print(f"   - Отсортированный: {sorted_numbers}")
            
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
