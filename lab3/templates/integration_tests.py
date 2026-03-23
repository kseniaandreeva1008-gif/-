"""
ИНТЕГРАЦИОННЫЕ ТЕСТЫ ДЛЯ РАБОТЫ С БАЗОЙ ДАННЫХ
Лабораторная работа №3 - Сортировка деревом (Tree Sort)
"""

import sqlite3
import random
import time
import os
from datetime import datetime

# Путь к тестовой базе данных (отдельная от основной)
TEST_DB = os.path.join(os.path.dirname(__file__), 'test_db.sqlite')


def init_test_db():
    """Инициализация тестовой базы данных"""
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()

    # Создаем таблицу пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # Создаем таблицу для массивов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS arrays(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            original TEXT,
            sorted TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Добавляем тестового пользователя
    cursor.execute("SELECT * FROM users WHERE username = 'test_user'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ('test_user', 'test_password')
        )

    conn.commit()
    conn.close()
    print("[OK] Тестовая база данных инициализирована")


def clear_test_db():
    """Очистка тестовой базы данных"""
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM arrays")
    conn.commit()
    conn.close()


def get_user_id():
    """Получить ID тестового пользователя"""
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = 'test_user'")
    user_id = cursor.fetchone()[0]
    conn.close()
    return user_id


def tree_sort(arr):
    """Алгоритм сортировки деревом"""
    if len(arr) <= 1:
        return arr
    root = arr[0]
    left = [x for x in arr[1:] if x < root]
    right = [x for x in arr[1:] if x >= root]
    return tree_sort(left) + [root] + tree_sort(right)


def generate_random_array(size, min_val=1, max_val=100):
    """Генерация случайного массива"""
    return [random.randint(min_val, max_val) for _ in range(size)]


def save_array_to_db(user_id, original):
    """Сохранение массива в базу данных"""
    try:
        conn = sqlite3.connect(TEST_DB)
        cursor = conn.cursor()
        sorted_arr = tree_sort(original)
        cursor.execute("""
            INSERT INTO arrays (user_id, original, sorted)
            VALUES (?, ?, ?)
        """, (user_id, ','.join(map(str, original)), ','.join(map(str, sorted_arr))))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[ОШИБКА] Сохранение не удалось: {e}")
        return False


def get_arrays_from_db():
    """Получение всех массивов из базы данных"""
    try:
        conn = sqlite3.connect(TEST_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT id, original, sorted FROM arrays")
        arrays = cursor.fetchall()
        conn.close()
        return arrays
    except Exception as e:
        print(f"[ОШИБКА] Загрузка не удалась: {e}")
        return []


def load_and_sort_from_db():
    """Загрузка массивов из БД и их сортировка"""
    arrays = get_arrays_from_db()
    if not arrays:
        return False, 0

    total_time = 0
    for arr_id, original_str, sorted_str in arrays:
        original = list(map(int, original_str.split(',')))

        start = time.time()
        sorted_arr = tree_sort(original)
        elapsed = time.time() - start
        total_time += elapsed

        # Проверяем, что сортировка правильная
        expected = sorted(original)
        if sorted_arr != expected:
            return False, total_time

    return True, total_time


def delete_all_arrays():
    """Удаление всех массивов из базы данных"""
    try:
        conn = sqlite3.connect(TEST_DB)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM arrays")
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[ОШИБКА] Удаление не удалось: {e}")
        return False


def get_array_count():
    """Получить количество массивов в базе данных"""
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM arrays")
    count = cursor.fetchone()[0]
    conn.close()
    return count


# ==================== ТЕСТЫ ====================

def test_add_arrays(array_size, array_count):
    """
    Тест добавления массивов в базу данных
    Тест добавления 100/1000/10000 массивов
    """
    print(f"\n{'=' * 60}")
    print(f"ТЕСТ A: Добавление {array_count} массивов по {array_size} элементов")
    print(f"{'=' * 60}")

    # Очищаем БД перед тестом
    clear_test_db()
    user_id = get_user_id()

    start_time = time.time()
    success_count = 0
    fail_count = 0

    for i in range(array_count):
        arr = generate_random_array(array_size)
        if save_array_to_db(user_id, arr):
            success_count += 1
        else:
            fail_count += 1

        # Прогресс
        if (i + 1) % 100 == 0:
            print(f"   Прогресс: {i + 1}/{array_count} массивов добавлено")

    elapsed = time.time() - start_time

    print(f"\nРЕЗУЛЬТАТЫ ТЕСТА A:")
    print(f"   Успешно добавлено: {success_count}")
    print(f"   Ошибок: {fail_count}")
    print(f"   Общее время: {elapsed:.4f} сек")
    print(f"   Среднее время на массив: {elapsed / array_count:.6f} сек")
    print(f"   Всего массивов в БД: {get_array_count()}")

    return success_count == array_count, elapsed


def test_load_and_sort(array_count):
    """
    Тест выгрузки и сортировки массивов из базы данных
    Тест выгрузки и сортировки случайных массивов
    """
    print(f"\n{'=' * 60}")
    print(f"ТЕСТ B: Выгрузка и сортировка {array_count} массивов")
    print(f"{'=' * 60}")

    start_time = time.time()
    success, total_time = load_and_sort_from_db()
    elapsed = time.time() - start_time

    print(f"\nРЕЗУЛЬТАТЫ ТЕСТА B:")
    print(f"   Успешность: {'ДА' if success else 'НЕТ'}")
    print(f"   Общее время: {elapsed:.4f} сек")
    print(f"   Среднее время на массив: {elapsed / array_count:.6f} сек")
    print(f"   Общее время сортировки (только алгоритм): {total_time:.4f} сек")

    return success, elapsed


def test_clear_db(array_count):
    """
    Тест очистки базы данных
    Тест очистки базы данных
    """
    print(f"\n{'=' * 60}")
    print(f"ТЕСТ C: Очистка базы данных ({array_count} записей)")
    print(f"{'=' * 60}")

    start_time = time.time()
    success = delete_all_arrays()
    elapsed = time.time() - start_time

    print(f"\nРЕЗУЛЬТАТЫ ТЕСТА C:")
    print(f"   Успешность: {'ДА' if success else 'НЕТ'}")
    print(f"   Общее время: {elapsed:.4f} сек")
    print(f"   Осталось записей в БД: {get_array_count()}")

    return success, elapsed


def run_all_tests():
    """
    Запуск всех интеграционных тестов
    """
    print("\n" + "=" * 70)
    print("ИНТЕГРАЦИОННЫЕ ТЕСТЫ ДЛЯ РАБОТЫ С БАЗОЙ ДАННЫХ")
    print("=" * 70)
    print(f"Дата и время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Инициализация тестовой БД
    init_test_db()

    # Параметры тестов
    test_sizes = [100, 1000, 10000]
    array_element_count = 50  # Размер каждого массива

    results = []

    for size in test_sizes:
        print(f"\n{'=' * 70}")
        print(f"ЗАПУСК ТЕСТОВ ДЛЯ {size} МАССИВОВ")
        print(f"{'=' * 70}")

        # Тест A: Добавление массивов
        success_a, time_a = test_add_arrays(array_element_count, size)

        if success_a:
            # Тест B: Выгрузка и сортировка
            success_b, time_b = test_load_and_sort(size)
        else:
            print("   [ПРЕДУПРЕЖДЕНИЕ] Тест B пропущен (тест A не выполнен)")
            success_b, time_b = False, 0

        # Тест C: Очистка базы данных
        success_c, time_c = test_clear_db(size)

        results.append({
            'size': size,
            'test_a': {'success': success_a, 'time': time_a},
            'test_b': {'success': success_b, 'time': time_b},
            'test_c': {'success': success_c, 'time': time_c}
        })

    # Вывод сводной таблицы
    print("\n" + "=" * 70)
    print("СВОДНАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ")
    print("=" * 70)
    print(f"{'Размер БД':<12} {'Тест A (добавление)':<25} {'Тест B (сортировка)':<25} {'Тест C (очистка)':<20}")
    print("-" * 82)

    for r in results:
        status_a = "[ДА]" if r['test_a']['success'] else "[НЕТ]"
        status_b = "[ДА]" if r['test_b']['success'] else "[НЕТ]"
        status_c = "[ДА]" if r['test_c']['success'] else "[НЕТ]"

        print(f"{r['size']:<12} {status_a} {r['test_a']['time']:.4f} сек        "
              f"{status_b} {r['test_b']['time']:.4f} сек        "
              f"{status_c} {r['test_c']['time']:.4f} сек")

    print("=" * 70)
    print("\nВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")

    # Сохранение результатов в файл
    save_results_to_file(results)

    return results


def save_results_to_file(results):
    """Сохранение результатов тестов в файл"""
    filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join(os.path.dirname(__file__), filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("РЕЗУЛЬТАТЫ ИНТЕГРАЦИОННЫХ ТЕСТОВ\n")
        f.write(f"Дата и время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")

        for r in results:
            f.write(f"\n--- ТЕСТ ДЛЯ {r['size']} МАССИВОВ ---\n")
            f.write(
                f"Тест A (добавление): {'УСПЕШНО' if r['test_a']['success'] else 'НЕУСПЕШНО'}, время: {r['test_a']['time']:.4f} сек\n")
            f.write(
                f"Тест B (сортировка): {'УСПЕШНО' if r['test_b']['success'] else 'НЕУСПЕШНО'}, время: {r['test_b']['time']:.4f} сек\n")
            f.write(
                f"Тест C (очистка): {'УСПЕШНО' if r['test_c']['success'] else 'НЕУСПЕШНО'}, время: {r['test_c']['time']:.4f} сек\n")

        f.write("\n" + "=" * 80 + "\n")

    print(f"\nРезультаты сохранены в файл: {filename}")


if __name__ == "__main__":
    try:
        # Запуск всех тестов
        run_all_tests()

        # Дополнительный тест: запуск 3 раза для каждого размера
        print("\n" + "=" * 70)
        print("ПОВТОРНЫЙ ЗАПУСК ТЕСТОВ (3 РАЗА ДЛЯ КАЖДОГО РАЗМЕРА)")
        print("=" * 70)

        test_sizes = [100, 1000, 10000]

        for size in test_sizes:
            print(f"\n{'=' * 50}")
            print(f"ТЕСТ ДЛЯ {size} МАССИВОВ (3 запуска)")
            print(f"{'=' * 50}")

            for run in range(1, 4):
                print(f"\n--- Запуск {run}/3 ---")
                init_test_db()
                clear_test_db()

                # Добавляем массивы
                user_id = get_user_id()
                for i in range(size):
                    arr = generate_random_array(50)
                    save_array_to_db(user_id, arr)

                # Тест B: выгрузка и сортировка
                success, elapsed = test_load_and_sort(size)
                print(f"  Результат запуска {run}: {'УСПЕШНО' if success else 'НЕУСПЕШНО'}, время: {elapsed:.4f} сек")

                # Очищаем
                delete_all_arrays()

    except KeyboardInterrupt:
        print("\n\nТесты прерваны пользователем")
    except Exception as e:
        print(f"\nОшибка при выполнении тестов: {e}")