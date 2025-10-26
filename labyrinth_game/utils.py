# labyrinth_game/utils.py

"""
Вспомогательные функции для игры 'Лабиринт сокровищ'.
Содержит функции для описания комнат, решения загадок и случайных событий.
"""

import math

from labyrinth_game.constant import (
    EVENT_PROBABILITY,
    NUM_EVENT_TYPES,
    ROOMS,
    TRAP_DAMAGE_THRESHOLD,
)


def pseudo_random(seed, modulo):
    """
    Генерирует псевдослучайное число в диапазоне [0, modulo) на основе seed.

    Args:
        seed (int): Базовое значение для генерации (например, количество шагов)
        modulo (int): Верхняя граница диапазона результата

    Returns:
        int: Псевдослучайное число в диапазоне [0, modulo)
    """
    x = math.sin(seed * 12.9898) * 43758.5453
    fractional_part = x - math.floor(x)
    result = fractional_part * modulo
    return int(result)


def trigger_trap(game_state):
    """
    Активирует ловушку с негативными последствиями для игрока.

    Args:
        game_state (dict): Текущее состояние игры
    """
    print("Ловушка активирована! Пол стал дрожать...")

    inventory = game_state["player_inventory"]

    if inventory:
        # Выбираем случайный предмет для удаления
        item_index = pseudo_random(game_state["steps_taken"], len(inventory))
        lost_item = inventory[item_index]
        inventory.remove(lost_item)
        print(f"Из-за тряски вы потеряли: {lost_item}!")
    else:
        # Если инвентарь пуст, игрок получает 'урон'
        chance = pseudo_random(game_state["steps_taken"], EVENT_PROBABILITY)
        if chance < TRAP_DAMAGE_THRESHOLD:
            print("Сильная тряска сбила вас с ног! Вы проиграли.")
            game_state["game_over"] = True
        else:
            print("Вам удалось удержаться на ногах!")


def random_event(game_state):
    """
    Обрабатывает случайные события, которые могут произойти при перемещении.

    Args:
        game_state (dict): Текущее состояние игры
    """
    # Проверяем, происходит ли событие
    event_chance = pseudo_random(game_state["steps_taken"], EVENT_PROBABILITY)
    if event_chance != 0:
        return  # Событие не происходит

    # Выбираем тип события
    event_type = pseudo_random(game_state["steps_taken"] + 1, NUM_EVENT_TYPES)

    current_room = game_state["current_room"]
    room_data = ROOMS[current_room]

    if event_type == 0:
        # Сценарий 1: Находка
        print("Вы заметили что-то блестящее на полу...")
        if "coin" not in room_data["items"]:
            room_data["items"].append("coin")
            print("Вы нашли монетку!")
        else:
            print("Но это оказалась всего лишь пыль.")

    elif event_type == 1:
        # Сценарий 2: Испуг
        print("Вы услышали подозрительный шорох...")
        if "sword" in game_state["player_inventory"]:
            print("Вы достали меч, и существо испугалось!")
        else:
            print("Шорох стих, но вы почувствовали беспокойство.")

    elif event_type == 2:
        # Сценарий 3: Срабатывание ловушки
        if (
            current_room == "trap_room"
            and "torch" not in game_state["player_inventory"]
        ):
            print("Вы не заметили ловушку в темноте!")
            trigger_trap(game_state)
        else:
            print("Показалось, что что-то щёлкнуло... но ничего не произошло.")


def describe_current_room(game_state):
    """
    Выводит описание текущей комнаты и её содержимого.

    Args:
        game_state (dict): Текущее состояние игры
    """
    current_room = game_state["current_room"]
    room_data = ROOMS[current_room]

    print(f"\n== {current_room.upper()} ==")
    print(room_data["description"])

    if room_data["items"]:
        print("Заметные предметы:", ", ".join(room_data["items"]))

    print("Выходы:", ", ".join(room_data["exits"].keys()))

    if room_data["puzzle"]:
        print("Кажется, здесь есть загадка (используйте команду solve).")


def solve_puzzle(game_state):
    """
    Обрабатывает решение загадки в текущей комнате.

    Args:
        game_state (dict): Текущее состояние игры
    """
    from labyrinth_game.player_actions import get_input

    current_room = game_state["current_room"]
    room_data = ROOMS[current_room]

    if not room_data["puzzle"]:
        print("Загадок здесь нет.")
        return

    question, answer = room_data["puzzle"]
    print(question)
    user_answer = get_input("Ваш ответ: ")

    # Нормализуем ответы для сравнения
    normalized_user_answer = user_answer.strip().lower()
    normalized_correct_answer = answer.strip().lower()

    # Создаем список возможных правильных ответов
    correct_answers = [normalized_correct_answer]

    # Добавляем альтернативные варианты ответов
    if current_room == "hall":
        correct_answers.extend(["10", "десять", "ten"])
    elif current_room == "library":
        correct_answers.extend(["огонь", "fire"])
    elif current_room == "trap_room":
        correct_answers.extend(["шаг шаг шаг", "step step step"])
    elif current_room == "treasure_room":
        correct_answers.extend(["10", "десять", "ten"])

    # Проверяем ответ
    if normalized_user_answer in correct_answers:
        print("Верно! Загадка решена.")
        room_data["puzzle"] = None

        # Награда за решение загадки зависит от комнаты
        if current_room == "hall":
            print("Вы получаете ключ от сокровищницы!")
            game_state["player_inventory"].append("treasure_key")
        elif current_room == "library":
            print("Вы нашли скрытый свиток с мудростью!")
        elif current_room == "trap_room":
            print("Ловушка деактивирована! Вы можете безопасно перемещаться.")
    else:
        print("Неверно. Попробуйте снова.")
        # В trap_room неверный ответ активирует ловушку
        if current_room == "trap_room":
            print("Неверный ответ активировал защитный механизм!")
            trigger_trap(game_state)


def attempt_open_treasure(game_state):
    """
    Попытка открыть сундук с сокровищами в treasure_room.

    Args:
        game_state (dict): Текущее состояние игры
    """
    from labyrinth_game.player_actions import get_input

    current_room = game_state["current_room"]
    room_data = ROOMS[current_room]
    inventory = game_state["player_inventory"]

    if "treasure_key" in inventory:
        print("Вы применяете ключ, и замок щёлкает. Сундук открыт!")
        if "treasure_chest" in room_data["items"]:
            room_data["items"].remove("treasure_chest")
        print("В сундуке сокровище! Вы победили!")
        game_state["game_over"] = True
    else:
        print("Сундук заперт. У вас нет ключа.")
        choice = get_input("Ввести код? (да/нет): ")
        if choice == "да":
            code = get_input("Введите код: ")
            if code == room_data["puzzle"][1]:
                print("Замок щёлкает! Сундук открыт!")
                if "treasure_chest" in room_data["items"]:
                    room_data["items"].remove("treasure_chest")
                print("В сундуке сокровище! Вы победили!")
                game_state["game_over"] = True
            else:
                print("Неверный код.")
        else:
            print("Вы отступаете от сундука.")


def show_help(commands):
    """
    Выводит справку по доступным командам.

    Args:
        commands (dict): Словарь с командами и их описаниями
    """
    print("\nДоступные команды:")
    for cmd, description in commands.items():
        # Форматируем команду с выравниванием влево и дополняем пробелами до 16 символов
        formatted_cmd = cmd.ljust(16)
        print(f"  {formatted_cmd} - {description}")
