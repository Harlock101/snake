# Simple Snake game using pyglet
# By Jan Orava

import random
import pyglet
from pyglet.window import key
from pyglet.gl import *


# -------------------------------------------------------------------------------------------------------------------- #
#                                                 CONSTANT DECLARATION                                                 #
# -------------------------------------------------------------------------------------------------------------------- #
TILE_SIZE = 40
GRID_WIDTH = 15
GRID_HEIGHT = 15
SNAKE_IMG_SIZE = 40
WINDOW_WIDTH = GRID_WIDTH * TILE_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * TILE_SIZE
WINDOW_TITLE = "Snake"
LABEL_GAME_OVER = pyglet.text.Label('Game over', color=(255, 0, 0, 255), font_name='Times New Roman', font_size=22,
                                    x=WINDOW_WIDTH // 2, y=WINDOW_HEIGHT // 2, anchor_x='center', anchor_y='center')
LABEL_PRESS_ENTER = pyglet.text.Label('Press ENTER to reset', color=(255, 0, 0, 255), font_name='Times New Roman',
                                      font_size=22, x=WINDOW_WIDTH // 2, y=WINDOW_HEIGHT // 2 - 25, anchor_x='center',
                                      anchor_y='center')
LABEL_PRESS_ESC = pyglet.text.Label('Press ESC to exit', color=(255, 0, 0, 255), font_name='Times New Roman',
                                    font_size=22, x=WINDOW_WIDTH // 2, y=WINDOW_HEIGHT // 2 - 50, anchor_x='center',
                                    anchor_y='center')
BACKGROUND = pyglet.graphics.OrderedGroup(0)
FOREGROUND = pyglet.graphics.OrderedGroup(1)
SNAKE_IMG_GRID = pyglet.image.ImageGrid(pyglet.image.load('Graphics/Snake.png'), 4, 4)


# -------------------------------------------------------------------------------------------------------------------- #
#                                                 VECTOR CLASS                                                         #
# -------------------------------------------------------------------------------------------------------------------- #
class Vector2D:
    """Two-dimensional vector represents position or direction"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y:
            return True
        return False

    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)


# -------------------------------------------------------------------------------------------------------------------- #
#                                                 FOOD CLASS                                                           #
# -------------------------------------------------------------------------------------------------------------------- #
class Food:
    def __init__(self):
        self.img = pyglet.sprite.Sprite(SNAKE_IMG_GRID[(0, 2)], batch=batch, group=FOREGROUND)
        self.img.scale = TILE_SIZE / SNAKE_IMG_SIZE
        self.position = Vector2D
        self.respawn()

    def respawn(self):
        """Finds free position and spawns food"""
        while True:
            self.position.x = random.randint(0, GRID_WIDTH - 1)
            self.position.y = random.randint(0, GRID_HEIGHT - 1)
            if not snake.at_this_pos(self.position):
                break
        self.img.x = self.position.x * TILE_SIZE
        self.img.y = self.position.y * TILE_SIZE


# -------------------------------------------------------------------------------------------------------------------- #
#                                                 SNAKE CLASS                                                          #
# -------------------------------------------------------------------------------------------------------------------- #
class Snake:
    body = []  # list of positions for each body part of snake
    images = []  # list of images for each body part of snake
    direction = Vector2D
    new_direction = Vector2D
    ate_food = bool

    def __init__(self):
        self.reset()

        self.head = {
            (0, 1): SNAKE_IMG_GRID[(3, 0)],   # head points UP
            (0, -1): SNAKE_IMG_GRID[(3, 2)],  # head points DOWN
            (1, 0): SNAKE_IMG_GRID[(3, 1)],   # head points RIGHT
            (-1, 0): SNAKE_IMG_GRID[(3, 3)],  # head points LEFT
        }

        self.tail = {
            (0, 1): SNAKE_IMG_GRID[(2, 0)],   # tail points UP, that means there is nothing beneath it
            (0, -1): SNAKE_IMG_GRID[(2, 2)],  # tail points DOWN
            (1, 0): SNAKE_IMG_GRID[(2, 1)],   # tail points RIGHT
            (-1, 0): SNAKE_IMG_GRID[(2, 3)],  # tail points LEFT
        }

        self.body_part = {
            (0, 2): SNAKE_IMG_GRID[(0, 0)],    # body points UP
            (0, -2): SNAKE_IMG_GRID[(0, 0)],   # body points DOWN
            (2, 0): SNAKE_IMG_GRID[(0, 1)],    # body points RIGHT
            (-2, 0): SNAKE_IMG_GRID[(0, 1)],   # body points LEFT
            (1, -1): SNAKE_IMG_GRID[(1, 2)],   # body points from DOWN to LEFT or from LEFT to DOWN
            (1, 1): SNAKE_IMG_GRID[(1, 3)],    # body points from UP to LEFT or from LEFT to UP
            (-1, -1): SNAKE_IMG_GRID[(1, 1)],  # body points from DOWN to RIGHT or from RIGHT to DOWN
            (-1, 1): SNAKE_IMG_GRID[(1, 0)],   # body points from UP to RIGHT or from RIGHT to UP
        }

    def draw(self):
        self.images = []
        for index, part in enumerate(self.body):
            if index == 0:  # at index 0 is always HEAD
                img = self.head[self.direction.x, self.direction.y]
            elif index == len(self.body) - 1:  # at last index is always TAIL
                if self.ate_food:
                    """
                    if it recently ate food, there is copy of last element,
                    so we need check one element before it, otherwise we get direction (0, 0)
                    """
                    tail_dir = self.body[index - 2] - part
                else:
                    tail_dir = self.body[index - 1] - part
                img = self.tail[tail_dir.x, tail_dir.y]
            else:
                if self.ate_food and index == len(self.body) - 2:  # skips copy if it recently ate food
                    continue
                body_dir = self.body[index - 1] - self.body[index + 1]
                # decides if we need reverse direction
                if part.x != self.body[index - 1].x:
                    body_dir.x *= -1
                    body_dir.y *= -1
                img = self.body_part[body_dir.x, body_dir.y]
            sprite = pyglet.sprite.Sprite(img, part.x * TILE_SIZE, part.y * TILE_SIZE, batch=batch, group=FOREGROUND)
            sprite.scale = TILE_SIZE / SNAKE_IMG_SIZE
            self.images.append(sprite)

    def update(self):
        self.ate_food = False
        self.direction = self.new_direction  # changes direction based on input from player
        self.body.insert(0, self.body[0] + self.direction)  # insert new HEAD based on direction
        del self.body[-1]  # deletes last body part
        self.check_collision()

    def reset(self):
        self.body = [Vector2D(GRID_WIDTH // 2, GRID_HEIGHT // 2),
                     Vector2D(GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2),
                     Vector2D(GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2)]
        self.direction = Vector2D(1, 0)  # RIGHT
        self.new_direction = Vector2D(1, 0)  # RIGHT
        self.ate_food = False

    def change_dir(self, direct):
        # check for opposite direction, e.g. if direction is LEFT then new direction can not be RIGHT
        if self.direction.x + direct.x != 0 or self.direction.x + direct.x != 0:
            self.new_direction = direct

    def check_collision(self):
        # check if snake is out of grid
        if self.body[0].x < 0 or self.body[0].x > GRID_WIDTH - 1 \
                or self.body[0].y < 0 or self.body[0].y > GRID_HEIGHT - 1:
            game_over()
        # check if HEAD is on the same spot as any bdy part
        for part in self.body[1:]:
            if part == self.body[0]:
                game_over()
        # check if snake ate food
        if self.body[0] == food.position:
            food.respawn()
            self.grow()

    def grow(self):
        global score
        score += 1
        self.ate_food = True
        copy = self.body[-1]  # copies last body part and insert to end
        self.body.insert(-1, copy)

    def at_this_pos(self, position):
        """
        # Checks if at given position is snake
        """
        for part in self.body:
            if part == position:
                return True
        return False


# -------------------------------------------------------------------------------------------------------------------- #
#                                                 FUNCTIONS                                                            #
# -------------------------------------------------------------------------------------------------------------------- #
def load_background():
    images = []
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            img = SNAKE_IMG_GRID[(0, 3)]
            x_pos = x * TILE_SIZE
            y_pos = y * TILE_SIZE
            sprite = pyglet.sprite.Sprite(img, x_pos, y_pos, batch=batch, group=BACKGROUND)
            sprite.scale = TILE_SIZE / SNAKE_IMG_SIZE
            images.append(sprite)
    return images


def update(dt):
    snake.update()


def reset_game():
    global snake, score, food
    score = 0
    snake.reset()
    food.respawn()


def game_over():
    global running
    pyglet.clock.unschedule(update)
    running = False


def print_lose_label():
    LABEL_GAME_OVER.draw()
    LABEL_PRESS_ENTER.draw()
    LABEL_PRESS_ESC.draw()


# -------------------------------------------------------------------------------------------------------------------- #
#                                                 MAIN FUNCTION                                                        #
# -------------------------------------------------------------------------------------------------------------------- #
def main():
    global running
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    pyglet.clock.schedule_interval(update, 0.2)
    running = True
    pyglet.app.run()


# -------------------------------------------------------------------------------------------------------------------- #
#                                                 GLOBAL VARIABLES                                                     #
# -------------------------------------------------------------------------------------------------------------------- #
window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
score = 0
label_score = pyglet.text.Label('Score: ' + str(score), color=(0, 0, 0, 255), font_name='Times New Roman', font_size=22,
                                x=0, y=WINDOW_HEIGHT - 22)
batch = pyglet.graphics.Batch()
running = False
background_images = load_background()

snake = Snake()
food = Food()


# -------------------------------------------------------------------------------------------------------------------- #
#                                                 WINDOW EVENTS                                                        #
# -------------------------------------------------------------------------------------------------------------------- #
@window.event
def on_draw():
    window.clear()
    snake.draw()
    batch.draw()
    label_score.text = 'Score: ' + str(score)
    label_score.draw()
    if not running:
        print_lose_label()


@window.event
def on_key_press(symbol, modifiers):
    global running
    if not running:
        if symbol == key.ENTER:  # player wants to play again
            reset_game()
            pyglet.clock.schedule_interval(update, 0.2)
            running = True
    else:
        if symbol == key.LEFT:
            snake.change_dir(Vector2D(-1, 0))
        elif symbol == key.UP:
            snake.change_dir(Vector2D(0, 1))
        elif symbol == key.RIGHT:
            snake.change_dir(Vector2D(1, 0))
        elif symbol == key.DOWN:
            snake.change_dir(Vector2D(0, -1))


# -------------------------------------------------------------------------------------------------------------------- #
#                                                 START GAME                                                           #
# -------------------------------------------------------------------------------------------------------------------- #
if __name__ == '__main__':
    main()
