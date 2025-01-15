import pygame
import sys
from random import choice, randint

# Константы
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SNAKE_COLOR = (0, 100, 0)
RED_APPLE_COLOR = (255, 0, 0)
GREEN_APPLE_COLOR = (173, 255, 47)
BACKGROUND_COLOR = (169, 169, 169)
FONT_COLOR = (0, 0, 0)
ALL_CELLS = {(x * GRID_SIZE, y * GRID_SIZE)
             for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)}

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Змейка")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)


class Snake:
    """Класс для представления змейки."""

    def __init__(self):
        """Инициализация змейки."""
        self.reset()

    def get_head_position(self):
        """Получить текущую позицию головы змейки."""
        return self.positions[0]

    def move(self):
        """
        Движение змейки.

        Возвращает:
            bool: True, если движение успешно, False в случае самоукуса.
        """
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = ((head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
                    (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT)

        if new_head in self.positions[2:]:
            self.positions = [new_head]
            return False

        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

        return True

    def reset(self):
        """Сброс состояния змейки."""
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = (0, -1)
        self.length = 1
        self.last = None

    def grow(self):
        """Увеличить длину змейки."""
        self.length += 1

    def draw(self, surface):
        """Отрисовать змейку."""
        for pos in self.positions:
            draw_cell(surface, pos, SNAKE_COLOR)


class Apple:
    """Класс для представления яблока."""

    def __init__(self, snake_positions, color):
        """
        Инициализация яблока.

        Параметры:
            snake_positions (list): Позиции тела змейки.
            color (tuple): Цвет яблока.
        """
        self.color = color
        self.position = self.random_position(snake_positions)

    def random_position(self, snake_positions):
        """
        Генерация случайной позиции яблока, исключая позиции змейки.

        Параметры:
            snake_positions (list): Позиции тела змейки.

        Возвращает:
            tuple: Новая позиция яблока.
        """
        available_cells = list(ALL_CELLS - set(snake_positions))
        return choice(available_cells)

    def draw(self, surface):
        """Отрисовать яблоко."""
        draw_cell(surface, self.position, self.color)


def draw_cell(surface, position, color):
    """Отрисовка отдельной клетки."""
    x, y = position
    pygame.draw.rect(surface, color, (x, y, GRID_SIZE, GRID_SIZE))


def draw_text(surface, text, position):
    """Отображение текста на экране."""
    label = font.render(text, True, FONT_COLOR)
    surface.blit(label, position)


def game_over_screen():
    """Экран окончания игры."""
    screen.fill(BACKGROUND_COLOR)
    draw_text(screen, "Вы проиграли!", (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 40))
    draw_text(screen, "Нажмите ПРОБЕЛ для рестарта",
              (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return


def main():
    """Главная функция игры."""
    high_score = 0

    while True:
        snake = Snake()
        red_apple = Apple(snake.positions, RED_APPLE_COLOR)
        green_apple = None
        score = 0
        speed = 10

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                    direction_map = {
                        pygame.K_UP: (0, -1),
                        pygame.K_DOWN: (0, 1),
                        pygame.K_LEFT: (-1, 0),
                        pygame.K_RIGHT: (1, 0),
                    }
                    new_direction = direction_map.get(event.key)
                    if new_direction and new_direction != (-snake.direction[0], -snake.direction[1]):
                        snake.direction = new_direction

            if not snake.move():
                break

            head_position = snake.get_head_position()

            if head_position == red_apple.position:
                snake.grow()
                red_apple.position = red_apple.random_position(snake.positions)
                score += 1
                speed += 1
                high_score = max(high_score, score)

                if randint(1, 4) == 1:
                    green_apple = Apple(snake.positions, GREEN_APPLE_COLOR)
                else:
                    green_apple = None

            if green_apple and head_position == green_apple.position:
                break

            screen.fill(BACKGROUND_COLOR)
            snake.draw(screen)
            red_apple.draw(screen)
            if green_apple:
                green_apple.draw(screen)

            draw_text(screen, f"Счет: {score}", (10, 10))
            draw_text(screen, f"Рекорд: {high_score}", (10, 40))

            pygame.display.flip()
            clock.tick(speed)

        game_over_screen()


if __name__ == "__main__":
    main()