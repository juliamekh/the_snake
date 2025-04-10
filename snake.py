from random import choice

import pygame

# Константы для размеров поля и сетки:
# по умолчанию поле (640, 480),
# сетка (32, 24) с шагом в 20
SCREEN_WIDTH, SCREEN_HEIGHT = 900, 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

GRID_CENTER_X = GRID_WIDTH // 2
GRID_CENTER_Y = GRID_HEIGHT // 2

ALL_CELLS = set(
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(0, GRID_WIDTH)
    for y in range(0, GRID_HEIGHT)
)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

NEXT_DIRECTION = {
    (pygame.K_UP, LEFT): UP,
    (pygame.K_DOWN, LEFT): DOWN,
    (pygame.K_UP, RIGHT): UP,
    (pygame.K_DOWN, RIGHT): DOWN,
    (pygame.K_LEFT, UP): LEFT,
    (pygame.K_RIGHT, UP): RIGHT,
    (pygame.K_RIGHT, DOWN): RIGHT,
    (pygame.K_LEFT, DOWN): LEFT
}


# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 64, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)
BAD_APPLE_COLOR = (200, 172, 64)
STONE_COLOR = (172, 172, 172)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

SNAKE_HEAD_COLOR = (0, 128, 0)

DEFAULT_COLOR = (255, 255, 255)
DEFAULT_POSITION = (0, 0)

# Скорость движения змейки (по умолчанию 20):
SPEED = 10
SPEED_DECREMENT = 2
# SPEED_BASE = min(SPEED, GRID_CENTER_X, GRID_CENTER_Y)

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
screen.fill(BOARD_BACKGROUND_COLOR)

# Заголовок окна игрового поля:
pygame.display.set_caption('Вообще крутая змейка!')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Описывает стандартный объект игры."""

    def __init__(
            self,
            position=DEFAULT_POSITION,
            body_color=DEFAULT_COLOR
    ):
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Абстрактный метод для отрисовки игрового объекта."""
        pass

    def draw_cell(self, position, color):
        """Метод для покраски одной клетки."""
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw_clear_cell(self, position, color):
        """Метод для покраски одной клетки в цвет фона."""
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)


class Apple(GameObject):
    """Описывает объект яблока."""

    def __init__(
            self,
            occupied: set[tuple[int, int]],
            body_color=APPLE_COLOR
    ):
        self.position = None
        super().__init__(
            position=self.randomize_position(occupied=occupied),
            body_color=body_color
        )

    def randomize_position(self, occupied: set[tuple[int, int]]):
        """Задает яблоку случайную позицию на игровом поле."""
        if self.position:
            old_position = self.position
            occupied.remove(old_position)
        new_position = choice(tuple(ALL_CELLS - occupied))
        self.position = new_position
        occupied.add(new_position)
        return self.position

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        self.draw_cell(self.position, self.body_color)


class BadApple(Apple):
    """Описывает объект "плохого" яблока."""

    def __init__(
        self,
        occupied_cells: set[tuple[int, int]],
        body_color=BAD_APPLE_COLOR
    ):
        super().__init__(
            occupied=occupied_cells,
            body_color=body_color
        )


class Stone(GameObject):
    """Описывает объект камня."""

    def __init__(
            self,
            occupied: set[tuple[int, int]],
            body_color=STONE_COLOR
    ):
        self.position = None
        self.position = self.randomize_position(occupied=occupied)
        self.body_color = body_color

    def randomize_position(self, occupied: set[tuple[int, int]]):
        """Задает случайную позицию на игровом поле."""
        # x_coord = randint(0, (GRID_WIDTH - 1)) * GRID_SIZE
        # y_coord = randint(0, (GRID_HEIGHT - 1)) * GRID_SIZE
        # self.position = (x_coord, y_coord)
        if self.position:
            old_position = self.position
            occupied.remove(old_position)
        new_position = choice(tuple(ALL_CELLS - occupied))
        self.position = new_position
        occupied.add(new_position)
        return self.position

    def draw(self):
        """Отрисовывает камень на игровом поле."""
        self.draw_cell(self.position, self.body_color)


class Snake(GameObject):
    """Описывает объект змейки."""

    def __init__(
            self,
            length=1,
            positions=[(GRID_CENTER_X * GRID_SIZE,
                        GRID_CENTER_Y * GRID_SIZE)],
            direction=RIGHT,
            next_direction=None,
            body_color=SNAKE_COLOR,
            speed=SPEED
    ):
        self.length = length
        self.positions = positions
        self.direction = direction
        self.next_direction = next_direction
        self.last = None
        self.speed = SPEED
        super().__init__(position=positions[0],
                         body_color=body_color)

    def update_direction(self):
        """Обновление направление после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def update_speed(self):
        """Обновление скорости после увеличения длины."""
        if self.length >= 50:
            self.speed = 5
        elif self.length >= 40:
            self.speed = 7
        elif self.length >= 30:
            self.speed = 10
        elif self.length >= 20:
            self.speed = 12
        elif self.length >= 10:
            self.speed = 15
        else:
            self.speed = 20

    def move(self):
        """Движение змейки вперед в направлении direction."""
        old_head = self.get_head_position()
        new_head_x = (old_head[0] + self.direction[0] * GRID_SIZE) \
            % (GRID_WIDTH * GRID_SIZE)
        new_head_y = (old_head[1] + self.direction[1] * GRID_SIZE) \
            % (GRID_HEIGHT * GRID_SIZE)
        self.position = (new_head_x, new_head_y)
        self.positions.insert(0, self.position)
        self.last = self.positions.pop()

    def draw(self):
        """Отрисовка змейки на игровом поле."""
        if self.length > 1:
            self.draw_cell(self.positions[1], self.body_color)

        # Отрисовка головы змейки
        self.draw_cell(self.position, SNAKE_HEAD_COLOR)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.position

    def reset(self):
        """Возвращает змейку в начальную позицию после поражения."""
        self.length = 1
        self.positions = [(GRID_CENTER_X * GRID_SIZE,
                           GRID_CENTER_Y * GRID_SIZE)]
        self.direction = choice([RIGHT, DOWN, LEFT, UP])
        self.next_direction = None
        self.position = self.positions[0]
        self.last = None
        screen.fill(BOARD_BACKGROUND_COLOR)


def handle_keys(game_object):
    """Обработка действий пользователя."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
            elif event.key == pygame.K_q:
                game_object.speed += SPEED_DECREMENT
            elif (
                event.key == pygame.K_w and game_object.speed > SPEED_DECREMENT
            ):
                game_object.speed -= SPEED_DECREMENT
            elif (event.key, game_object.direction) in NEXT_DIRECTION.keys():
                game_object.next_direction = NEXT_DIRECTION[
                    (event.key, game_object.direction)
                ]


def reset_game(
        occupied: set[tuple[int, int]],
        snake: Snake,
        apple: Apple,
        bad_apple: BadApple,
        stone: Stone
):
    """Запускает игру с начала."""
    snake.reset()
    clear_all_positions(apple=apple, bad_apple=bad_apple, stone=stone)
    occupied = get_occupied(snake, apple, bad_apple, stone)
    randomize_all_positions(
        occupied_positions=occupied,
        apple=apple,
        bad_apple=bad_apple,
        stone=stone
    )
    occupied = get_occupied(snake, apple, bad_apple, stone)
    # free_cells = ALL_CELLS - get_occupied(snake, apple, bad_apple, stone)


def randomize_all_positions(
        occupied_positions: set[tuple[int, int]],
        apple: Apple,
        bad_apple: BadApple,
        stone: Stone
):
    """
    Перемещает яблоко, "плохое" яблоко и камень в случайные
    позиции.
    """
    apple.randomize_position(occupied_positions)
    bad_apple.randomize_position(occupied_positions)
    stone.randomize_position(occupied_positions)


def clear_all_positions(
    apple: Apple,
    bad_apple: BadApple,
    stone: Stone
):
    """Закрашивает старые позиции яблока, "плохого яблока" и камня."""
    apple.draw_clear_cell(apple.position, BOARD_BACKGROUND_COLOR)
    bad_apple.draw_clear_cell(bad_apple.position, BOARD_BACKGROUND_COLOR)
    stone.draw_clear_cell(stone.position, BOARD_BACKGROUND_COLOR)


def get_occupied(
    snake: Snake,
    apple: Apple,
    bad_apple: BadApple,
    stone: Stone
):
    """Возвращает набор занятых клеток на поле."""
    occupied = set(position for position in snake.positions)
    occupied.add(apple.position)
    occupied.add(bad_apple.position)
    occupied.add(stone.position)
    return occupied


def get_record_data():
    """
    Читает рекорд из бинарного файла.
    Если не находит файл, то создает с рекордом 0.
    """
    try:
        records = open('records.bin', 'r')
        record = int(records.read())
        records.close()
        return record
    except OSError:
        records = open('records.bin', 'x')
        records.write('0')
        records.close()
        return 0


def set_record_data(record_score):
    """
    Записывает рекорд в бинарный файл.
    Если не находит файл, то создает.
    """
    records = open('records.bin', 'w')
    records.write(str(record_score))
    records.close()


def main():
    """Основная функция игрового процесса."""
    # Инициализация PyGame:
    pygame.init()
    # Тут нужно создать экземпляры классов.
    snake = Snake()
    # ##################################################
    # УЖЕ ПОСЛЕ ИЗМЕНЕНИЯ БЫЛ ПОДЛОВЛЕН НА СПАУНЕ ПРЕДМЕТА НА ЗМЕЕ
    occupied_cells = set(snake.positions)
    apple = Apple(occupied_cells)
    occupied_cells.add(apple.position)
    bad_apple = BadApple(occupied_cells)
    occupied_cells.add(bad_apple.position)
    stone = Stone(occupied_cells)
    score_record = get_record_data()
    score = 0

    while True:
        clock.tick(snake.speed)

        # Тут опишите основную логику игры.
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        occupied_cells = get_occupied(snake, apple, bad_apple, stone)
        if snake.get_head_position() == apple.position:
            clear_all_positions(
                apple=apple,
                bad_apple=bad_apple,
                stone=stone
            )

            snake.length += 1
            score += 1
            snake.positions.append(snake.last)
            occupied_cells.add(snake.last)
            randomize_all_positions(
                occupied_positions=occupied_cells,
                apple=apple,
                bad_apple=bad_apple,
                stone=stone)
        elif snake.get_head_position() == bad_apple.position:
            snake.length -= 1
            score = 0 if score < 1 else score - 1
            if snake.last:
                snake.draw_clear_cell(snake.last, BOARD_BACKGROUND_COLOR)
            if snake.length < 1:
                reset_game(
                    occupied=occupied_cells,
                    snake=snake,
                    apple=apple,
                    bad_apple=bad_apple,
                    stone=stone
                )
                # occupied_cells = get_occupied(snake, apple, bad_apple, stone)
                score = 0
            else:
                snake.last = snake.positions.pop()
                # occupied_cells = get_occupied(snake, apple, )
                occupied_cells -= set(snake.last)
                clear_all_positions(
                    apple=apple,
                    bad_apple=bad_apple,
                    stone=stone
                )
                randomize_all_positions(
                    occupied_positions=occupied_cells,
                    apple=apple,
                    bad_apple=bad_apple,
                    stone=stone
                )
        if len(set(snake.positions)) != snake.length \
           or snake.get_head_position() == stone.position:
            reset_game(
                occupied=occupied_cells,
                snake=snake,
                apple=apple,
                bad_apple=bad_apple,
                stone=stone
            )
            # occupied_cells = get_occupied(snake, apple, bad_apple, stone)
            score = 0
        snake.draw()
        apple.draw()
        bad_apple.draw()
        stone.draw()
        if snake.length < 50:
            snake.update_speed()
        if score > score_record:
            score_record = score
            set_record_data(score_record)
        pygame.display.update()
        pygame.display.set_caption(
            'Вообще крутая змейка! '
            f'Текущая скорость: {snake.speed} '
            f'Счет: {score} '
            f'Рекорд: {score_record}'
        )


if __name__ == '__main__':
    main()


# Метод draw класса Apple
# def draw(self):
#     rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
#     pygame.draw.rect(screen, self.body_color, rect)
#     pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

# # Метод draw класса Snake
# def draw(self):
#     for position in self.positions[:-1]:
#         rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
#         pygame.draw.rect(screen, self.body_color, rect)
#         pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

#     # Отрисовка головы змейки
#     head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
#     pygame.draw.rect(screen, self.body_color, head_rect)
#     pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

#     # Затирание последнего сегмента
#     if self.last:
#         last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
#         pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

# Функция обработки действий пользователя
# def handle_keys(game_object):
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             pygame.quit()
#             raise SystemExit
#         elif event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_UP and game_object.direction != DOWN:
#                 game_object.next_direction = UP
#             elif event.key == pygame.K_DOWN
#                  and game_object.direction != UP:
#                 game_object.next_direction = DOWN
#             elif event.key == pygame.K_LEFT
#                  and game_object.direction != RIGHT:
#                 game_object.next_direction = LEFT
#             elif event.key == pygame.K_RIGHT
#                  and game_object.direction != LEFT:
#                 game_object.next_direction = RIGHT

# Метод обновления направления после нажатия на кнопку
# def update_direction(self):
#     if self.next_direction:
#         self.direction = self.next_direction
#         self.next_direction = None
