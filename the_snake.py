import pygame
import sys
from random import choice, randint

# Константы для игры
SCREEN_WIDTH, SCREEN_HEIGHT = 400, 400
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SNAKE_COLOR = (0, 100, 0)
APPLE_RED_COLOR = (255, 0, 0)
APPLE_GREEN_COLOR = (173, 255, 47)
BOARD_BACKGROUND_COLOR = (169, 169, 169)
TEXT_COLOR = (0, 0, 0)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Все ячейки поля
ALL_CELLS = {
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
}

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, position=(0, 0), color=(255, 255, 255)):
        self.position = position
        self.color = color

    def draw(self, surface):
        """Рисует объект на экране."""
        draw_cell(surface, self.position, self.color)


class Apple(GameObject):
    """Класс для яблок."""

    def __init__(self, snake_segments=None, color=APPLE_RED_COLOR):
        if snake_segments is None:
            snake_segments = []
        position = self.random_position(snake_segments)
        super().__init__(position, color)

    def random_position(self, snake_segments):
        """Выбирает случайную позицию для яблока."""
        available_cells = list(ALL_CELLS - set(snake_segments))
        return choice(available_cells)


class Snake(GameObject):
    """Класс, представляющий змейку."""

    def __init__(self):
        self.segments = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = UP
        self.length = 1
        self.color = SNAKE_COLOR

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.segments[0]

    def move(self):
        """Перемещает змейку и проверяет столкновения."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )
        if new_head in self.segments[2:]:
            return False

        self.segments.insert(0, new_head)
        if len(self.segments) > self.length:
            self.segments.pop()
        return True

    def reset(self):
        """Сбрасывает состояние змейки."""
        self.segments = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = UP
        self.length = 1

    def grow(self):
        """Увеличивает длину змейки."""
        self.length += 1

    def draw(self, surface):
        """Рисует змейку на экране."""
        for segment in self.segments:
            draw_cell(surface, segment, self.color)


def draw_cell(surface, position, color):
    """Рисует одну клетку на экране."""
    x, y = position
    pygame.draw.rect(surface, color, (x, y, GRID_SIZE, GRID_SIZE))


def draw_text(surface, text, position):
    """Рисует текст на экране."""
    label = font.render(text, True, TEXT_COLOR)
    surface.blit(label, position)


def game_over_screen():
    """Показывает экран завершения игры."""
    screen.fill(BOARD_BACKGROUND_COLOR)
    draw_text(
        screen,
        "Game Over!",
        (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 40)
    )
    draw_text(
        screen,
        "Press SPACE to restart",
        (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2)
    )
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return


def handle_keys(snake):
    """Обрабатывает события клавиатуры."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            directions = {
                pygame.K_UP: UP,
                pygame.K_DOWN: DOWN,
                pygame.K_LEFT: LEFT,
                pygame.K_RIGHT: RIGHT,
            }
            new_d = directions.get(event.key)
            if new_d and new_d != (-snake.direction[0], -snake.direction[1]):
                snake.direction = new_d


def main_game_loop(high_score):
    """Основной игровой цикл."""
    snake = Snake()
    red_apple = Apple(snake.segments, APPLE_RED_COLOR)
    green_apple = None
    score = 0
    speed = 10

    while True:
        handle_keys(snake)

        if not snake.move():
            break

        head_position = snake.get_head_position()

        if head_position == red_apple.position:
            snake.grow()
            red_apple.position = red_apple.random_position(snake.segments)
            score += 1
            speed += 1
            high_score = max(high_score, score)

            if randint(1, 4) == 1:
                green_apple = Apple(snake.segments, APPLE_GREEN_COLOR)
            else:
                green_apple = None

        if green_apple and head_position == green_apple.position:
            break

        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw(screen)
        red_apple.draw(screen)
        if green_apple:
            green_apple.draw(screen)

        draw_text(screen, f"Score: {score}", (10, 10))
        draw_text(screen, f"High Score: {high_score}", (10, 40))

        pygame.display.flip()
        clock.tick(speed)

    return high_score


def main():
    """Главная функция игры."""
    high_score = 0
    while True:
        high_score = main_game_loop(high_score)
        game_over_screen()


if __name__ == "__main__":
    main()
