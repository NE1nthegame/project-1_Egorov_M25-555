# labyrinth_game/main.py

"""
Главный модуль игры 'Лабиринт сокровищ'.
Содержит точку входа, игровой цикл и обработку команд.
"""

from labyrinth_game.constant import COMMANDS, ROOMS
from labyrinth_game.player_actions import (
    get_input,
    move_player,
    show_inventory,
    take_item,
    use_item,
)
from labyrinth_game.utils import (
    attempt_open_treasure,
    describe_current_room,
    show_help,
    solve_puzzle,
)

# Глобальное состояние игры
game_state = {
    "player_inventory": [],  # Инвентарь игрока
    "current_room": "entrance",  # Текущая комната
    "game_over": False,  # Флаг окончания игры
    "steps_taken": 0,  # Количество шагов
}


def process_command(game_state, command):
    """
    Обрабатывает команду, введенную пользователем.

    Args:
        game_state (dict): Текущее состояние игры
        command (str): Команда для обработки
    """
    parts = command.split()
    if not parts:
        return

    cmd = parts[0]
    arg = parts[1] if len(parts) > 1 else None

    # Обработка односложных команд движения
    if cmd in ["north", "south", "east", "west"]:
        move_player(game_state, cmd)
        return

    match cmd:
        case "look":
            describe_current_room(game_state)
        case "go":
            if arg:
                move_player(game_state, arg)
            else:
                print("Укажите направление (north, south, east, west)")
        case "take":
            if arg:
                if arg == "treasure_chest":
                    print("Вы не можете поднять сундук, он слишком тяжелый.")
                else:
                    take_item(game_state, arg)
            else:
                print("Укажите предмет для взятия")
        case "use":
            if arg:
                use_item(game_state, arg)
            else:
                print("Укажите предмет для использования")
        case "inventory":
            show_inventory(game_state)
        case "solve":
            if game_state["current_room"] == "treasure_room":
                attempt_open_treasure(game_state)
            else:
                solve_puzzle(game_state)
        case "help":
            show_help(COMMANDS)
        case "quit" | "exit":
            print("Спасибо за игру!")
            game_state["game_over"] = True
        case _:
            print("Неизвестная команда. Введите 'help' для справки.")


def main():
    """
    Главная функция игры. Запускает игровой цикл.
    """
    # Приветственное сообщение
    print("Добро пожаловать в Лабиринт сокровищ!")

    # Описание стартовой комнаты
    describe_current_room(game_state)

    # Основной игровой цикл
    while not game_state["game_over"]:
        # Считываем команду от пользователя
        command = get_input("\nЧто вы хотите сделать? ")

        # Обрабатываем команду
        process_command(game_state, command)

        # Проверка условий победы
        if (
            game_state["current_room"] == "treasure_room"
            and "treasure_chest" not in ROOMS["treasure_room"]["items"]
        ):
            print("\n🎉 Поздравляем! Вы нашли сокровище и победили! 🎉")
            print(f"Количество шагов: {game_state['steps_taken']}")
            game_state["game_over"] = True


# Стандартная конструкция для запуска main()
if __name__ == "__main__":
    main()
