"""
The Snake game is an educational project.

Cohort: 43_python_plus.
Performed by: Alexander Myasoed.
Telegram: @Aleksandr_Myasoed.
"""
from abc import abstractmethod
from random import randint
import pygame as pg
from typing import List, Tuple, Optional

# Constants for field and grid sizes.
SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 480
GRID_SIZE: int = 20
GRID_WIDTH: int = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // GRID_SIZE

# Directions of movement.
UP: Tuple[int, int] = (0, -1)
DOWN: Tuple[int, int] = (0, 1)
LEFT: Tuple[int, int] = (-1, 0)
RIGHT: Tuple[int, int] = (1, 0)

# The background color is black.
BOARD_BACKGROUND_COLOR: Tuple[int, int, int] = (0, 0, 0)

# The default color of the object.
DEFAULT_COLOR: Tuple[int, int, int] = (255, 255, 255)

# The color of the cell border.
BORDER_COLOR: Tuple[int, int, int] = (93, 216, 228)

# The color of the apple.
APPLE_COLOR: Tuple[int, int, int] = (255, 0, 0)

# The color of the snake.
SNAKE_COLOR: Tuple[int, int, int] = (0, 255, 0)

# The speed of the snake's movement.
SPEED: int = 20

# Setting up the game window.
screen: pg.Surface = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Time setting.
clock: pg.time.Clock = pg.time.Clock()


class GameObject:
    """Base class for game objects."""

    def __init__(self, position: Tuple[int, int] = (0, 0),
                 body_color: Tuple[int, int, int] = DEFAULT_COLOR) -> None:
        """
        Initialization of the game object.

        Args:
            position (tuple): The position of the object on the playing field.
            body_color (tuple): The color of the object in RGB format.
        """
        self.position: Tuple[int, int] = position
        self.body_color: Tuple[int, int, int] = body_color

    @abstractmethod
    def draw(self) -> None:
        """Drawing a game object."""
        raise NotImplementedError(
            "The draw() method must be redefined in child classes"
        )


class Snake(GameObject):
    """A class describing a snake."""

    def __init__(self) -> None:
        """Snake initialization."""
        super().__init__((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), SNAKE_COLOR)
        self.speed: int = SPEED
        self.paused: bool = False
        self.game_over: bool = False
        self.direction: Tuple[int, int] = RIGHT
        self.next_direction: Optional[Tuple[int, int]] = None
        self.length: int = 1
        self.positions: List[Tuple[int, int]] = [self.position]
        self.last: Optional[Tuple[int, int]] = None

    def update_direction(self) -> None:
        """Updating the direction after pressing the button."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def is_game_over(self, next_position: Tuple[int, int]) -> None:
        """Checking that the snake did not crash into its tail."""
        if next_position in self.positions[2:]:
            self.game_over = True

    def move(self) -> Tuple[int, int]:
        """Calculating the new position of the Snake."""
        self.update_direction()
        x, y = self.position
        dx, dy = self.direction
        new_x = (x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (y + dy * GRID_SIZE) % SCREEN_HEIGHT
        next_position = (new_x, new_y)
        return next_position

    def insert_next_position(self, next_position: Tuple[int, int]) -> None:
        """Insert a new position into the Snake's body."""
        self.position = next_position
        self.positions.insert(0, self.position)

    def del_last_segment(self) -> None:
        """Remove the last segment of the snake from the positions list."""
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def reset(self) -> None:
        """Reset the snake to its initial state."""
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.last = None

    def get_head_position(self) -> Tuple[int, int]:
        """Get the position of the snake's head."""
        return self.positions[0]

    def get_length(self) -> int:
        """Calculate the length of the Snake."""
        return len(self.positions)

    def draw(self) -> None:
        """Drawing a snake."""
        for position in self.positions:
            rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, self.body_color, rect)
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Mashing the last segment.
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)


class Apple(GameObject):
    """A class describing an apple."""

    def __init__(
            self,
            snake_positions: List[Tuple[int, int]] = [(0, 0)]) -> None:
        """Initializing the apple."""
        super().__init__(position=(0, 0), body_color=APPLE_COLOR)
        self.snake_positions: List[Tuple[int, int]] = snake_positions
        self.randomize_position()

    def generate_new_position(self) -> Tuple[int, int]:
        """The function generates a new random position that is not occupied by the Snake."""
        while True:
            x = randint(0, GRID_WIDTH - 1)
            y = randint(0, GRID_HEIGHT - 1)
            new_position = (x * GRID_SIZE, y * GRID_SIZE)
            if new_position not in self.snake_positions:
                return new_position

    def randomize_position(self) -> None:
        """Generating a random apple position on the playing field."""
        self.position = self.generate_new_position()

    def draw(self) -> None:
        """Rendering an apple."""
        rect = pg.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


def handle_keys(snake: Snake) -> bool:
    """Processing user input."""
    direction_mapping = {
        pg.K_UP: UP,
        pg.K_DOWN: DOWN,
        pg.K_LEFT: LEFT,
        pg.K_RIGHT: RIGHT,
    }

    for event in pg.event.get():
        if event.type == pg.QUIT:
            return False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                snake.paused = not snake.paused
            else:
                new_direction = direction_mapping.get(event.key, None)
                if new_direction and (
                    (snake.direction == UP and new_direction != DOWN)
                    or (snake.direction == DOWN and new_direction != UP)
                    or (snake.direction == LEFT and new_direction != RIGHT)
                    or (snake.direction == RIGHT and new_direction != LEFT)
                ):
                    snake.next_direction = new_direction
    return True


def main() -> None:
    """Main function."""
    pg.init()
    snake = Snake()
    apple = Apple(snake.positions)
    running = True
    while running:
        clock.tick(snake.speed)
        screen.fill(BOARD_BACKGROUND_COLOR)
        running = handle_keys(snake)
        if not (snake.game_over or snake.paused):
            next_position = snake.move()
            snake.is_game_over(next_position)
            snake.insert_next_position(next_position)
            snake.del_last_segment()
            if snake.position == apple.position:
                snake.length += 1
                if snake.speed < 100:
                    snake.speed += 1
                apple.position = apple.generate_new_position()
        snake.draw()
        apple.draw()
        if snake.game_over:
            pg.display.set_caption(
                f'Игра окончена! | Скорость: {snake.speed} | '
                f'Длина: {snake.get_length()}'
            )
        elif snake.paused:
            pg.display.set_caption(
                f'Пауза! | Скорость: {snake.speed} | '
                f'Длина: {snake.get_length()}'
            )
        else:
            pg.display.set_caption(
                f'Змейка | Скорость: {snake.speed} | '
                f'Длина: {snake.get_length()}'
            )
        pg.display.update()
        clock.tick(snake.speed)
    pg.quit()


if __name__ == '__main__':
    main()