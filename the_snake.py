from random import choice, randint

import pygame as pg

# Инициализация pg:
pg.init()

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Инициализация родительского класса."""

    def __init__(self, body_color=BORDER_COLOR) -> None:
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def draw(self):
        """Пустая функция нужна для ипользования в объектах класса."""
        raise NotImplementedError('Метод для экземпляров класса')


class Apple(GameObject):
    """Создание экземпляра класса: Яблоко"""

    def __init__(self, body_color=APPLE_COLOR):
        super().__init__(body_color)

    def randomize_position(self, snake_position):
        """Метод для получения рандомной позиции яблока."""
        self.position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )
        while self.position in snake_position:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )

    def draw(self, surface):
        """Метод отрисовки яблока на экране."""
        rect = pg.Rect(
            (self.position[0], self.position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pg.draw.rect(surface, self.body_color, rect)
        pg.draw.rect(surface, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Экземпляр класса: Змейка."""

    def __init__(self, length=1, direction=RIGHT,
                 next_direction=None, body_color=(SNAKE_COLOR)):
        super().__init__(body_color)
        self.next_direction = next_direction
        self.last = None
        self.reset()

    def update_direction(self):
        """Метод обновления направления после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Метод обновляет позицию змейки (координаты каждой секции),
        добавляя новую голову в начало списка positions и удаляя
        последний элемент, если длина змейки не увеличилась.
        """
        head_position = self.get_head_position()
        x_cord = ((head_position[0] + self.direction[0] * GRID_SIZE)
                  % SCREEN_WIDTH)
        y_cord = ((head_position[1] + self.direction[1] * GRID_SIZE)
                  % SCREEN_HEIGHT)
        new_position = (x_cord, y_cord)
        self.positions.insert(0, (new_position))
        if len(self.positions) > self.length:
            self.last = self.positions[-1]
            self.positions.pop(-1)

    def draw(self, surface):
        """Метод отрисовки змейки на экране."""
        head_rect = pg.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(surface, self.body_color, head_rect)
        pg.draw.rect(surface, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента.
        if self.last:
            last_rect = pg.Rect(
                (self.last[0], self.last[1]),
                (GRID_SIZE, GRID_SIZE)
            )
            pg.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

    # Функция возвращает место положения головы змеи.
    def get_head_position(self):
        """Метод определяющий позицию головы змейки."""
        return self.positions[0]

    def reset(self):
        """Метод описывающий действие при столкновении змейки"""
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = choice([RIGHT, LEFT, UP, DOWN])
        screen.fill(BOARD_BACKGROUND_COLOR)


def handle_keys(game_object):
    """Функция описывающая нажатие клавиш"""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    raise SystemExit


def main():
    """Главная функция игры описывающая логику"""
    snake = Snake()
    apple = Apple()
    apple.randomize_position(snake.positions)

    while True:
        clock.tick(SPEED)

        apple.draw(screen)

        handle_keys(snake)
        snake.update_direction()
        """Вызов функции отвечающий за движение змейки."""
        snake.move()

        """Условие для увеличение змейки если она съела яблоко."""
        if snake.get_head_position() == apple.position:
            apple.randomize_position(snake.positions)
            snake.length += 1
        """Проверка на столкновение змейки."""
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
        """Отрисовать змейку."""
        snake.draw(screen)

        pg.display.update()


if __name__ == '__main__':
    main()