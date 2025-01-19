import pygame
import sys
from random import choice, randint

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
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
ALL_CELLS = {
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
}

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)


class GameObject:
    def __init__(self, position, body_color):
        self.position = position
        self.body_color = body_color

    def draw(self, surface):
        draw_cell(surface, self.position, self.body_color)


class Snake(GameObject):
    def __init__(self):
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = UP
        self.length = 1
        self.body_color = SNAKE_COLOR

    def get_head_position(self):
        return self.positions[0]

    def move(self):
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )
        if new_head in self.positions[2:]:
            return False

        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()
        return True

    def reset(self):
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = UP
        self.length = 1

    def grow(self):
        self.length += 1

    def draw(self, surface):
        for position in self.positions:
            draw_cell(surface, position, self.body_color)


class Apple(GameObject):
    def __init__(self, snake_positions, color):
        position = self.random_position(snake_positions)
        super().__init__(position, color)

    def random_position(self, snake_positions):
        available_cells = list(ALL_CELLS - set(snake_positions))
        return choice(available_cells)


def draw_cell(surface, position, color):
    x, y = position
    pygame.draw.rect(surface, color, (x, y, GRID_SIZE, GRID_SIZE))


def draw_text(surface, text, position):
    label = font.render(text, True, FONT_COLOR)
    surface.blit(label, position)


def game_over_screen():
    screen.fill(BACKGROUND_COLOR)
    draw_text(screen, "Game Over!", (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 40))
    draw_text(
        screen, "Press SPACE to restart", (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2)
    )
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return


def handle_events(snake):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            direction_map = {pygame.K_UP: UP, pygame.K_DOWN: DOWN, pygame.K_LEFT: LEFT, pygame.K_RIGHT: RIGHT}
            new_direction = direction_map.get(event.key)
            if new_direction and new_direction != (-snake.direction[0], -snake.direction[1]):
                snake.direction = new_direction


def main_game_loop(high_score):
    snake = Snake()
    red_apple = Apple(snake.positions, RED_APPLE_COLOR)
    green_apple = None
    score = 0
    speed = 10

    while True:
        handle_events(snake)

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

        draw_text(screen, f"Score: {score}", (10, 10))
        draw_text(screen, f"High Score: {high_score}", (10, 40))

        pygame.display.flip()
        clock.tick(speed)

    return high_score


def main():
    high_score = 0
    while True:
        high_score = main_game_loop(high_score)
        game_over_screen()


if __name__ == "__main__":
    main()
