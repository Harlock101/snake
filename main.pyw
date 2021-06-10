import random
import pyglet
from pyglet.window import key
from pyglet.gl import *


def load_background():
    for y in range(grid_height):
        for x in range(grid_width):
            img = snake_grid[(0, 3)]
            x_pos = x * tile_size
            y_pos = y * tile_size
            sprite = pyglet.sprite.Sprite(img, x_pos, y_pos, batch=batch, group=background)
            sprite.scale = tile_size / image_size
            background_images.append(sprite)


def update(dt):
    snake.update()


def game_over():
    print("Game over")
    exit(666)


class Vector2D:
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


class Food:
    def __init__(self):
        self.img = pyglet.sprite.Sprite(snake_grid[(0, 2)], batch=batch, group=foreground)
        self.img.scale = tile_size / image_size
        self.position = Vector2D(0, 0)
        self.respawn()

    def respawn(self):
        while True:
            self.position.x = random.randint(0, grid_width - 1)
            self.position.y = random.randint(0, grid_height - 1)
            if not snake.at_this_pos(self.position):
                break
        self.img.x = self.position.x * tile_size
        self.img.y = self.position.y * tile_size


class Snake:
    def __init__(self):
        self.body = [Vector2D(grid_width//2, grid_height//2),
                     Vector2D(grid_width//2 - 1, grid_height//2),
                     Vector2D(grid_width//2 - 2, grid_height//2)]
        self.direction = Vector2D(1, 0)
        self.new_direction = Vector2D(1, 0)
        self.ate_food = False

        self.head = {
            (0, 1): snake_grid[(3, 0)],
            (0, -1): snake_grid[(3, 2)],
            (1, 0): snake_grid[(3, 1)],
            (-1, 0): snake_grid[(3, 3)],
        }

        self.tail = {
            (0, 1): snake_grid[(2, 0)],
            (0, -1): snake_grid[(2, 2)],
            (1, 0): snake_grid[(2, 1)],
            (-1, 0): snake_grid[(2, 3)],
        }

        self.body_part = {
            (0, 2): snake_grid[(0, 0)],
            (0, -2): snake_grid[(0, 0)],
            (2, 0): snake_grid[(0, 1)],
            (-2, 0): snake_grid[(0, 1)],
            (1, -1): snake_grid[(1, 2)],
            (1, 1): snake_grid[(1, 3)],
            (-1, -1): snake_grid[(1, 1)],
            (-1, 1): snake_grid[(1, 0)],
        }

    def draw(self):
        images = []
        for index, part in enumerate(self.body):
            if index == 0:
                img = self.head[self.direction.x, self.direction.y]
            elif index == len(self.body) - 1:
                if self.ate_food:
                    tail_dir = self.body[index - 2] - part
                else:
                    tail_dir = self.body[index - 1] - part
                img = self.tail[tail_dir.x, tail_dir.y]
            else:
                if self.ate_food and index == len(self.body) - 2:
                    continue
                if part.x == self.body[index-1].x:
                    body_dir = self.body[index - 1] - self.body[index + 1]
                else:
                    body_dir = self.body[index + 1] - self.body[index - 1]
                img = self.body_part[body_dir.x, body_dir.y]
            sprite = pyglet.sprite.Sprite(img, part.x * tile_size, part.y * tile_size, batch=batch, group=foreground)
            sprite.scale = tile_size / image_size
            images.append(sprite)
        batch.draw()

    def update(self):
        self.ate_food = False
        self.direction = self.new_direction
        self.body.insert(0, self.body[0] + self.direction)
        del self.body[-1]
        self.check_collision()

    def change_dir(self, direct):
        if self.direction.x + direct.x != 0 or self.direction.x + direct.x != 0:
            self.new_direction = direct

    def check_collision(self):
        if self.body[0].x < 0 or self.body[0].x > grid_width - 1 \
                or self.body[0].y < 0 or self.body[0].y > grid_height - 1:
            game_over()
        for part in self.body[1:]:
            if part == self.body[0]:
                game_over()
        if self.body[0] == food.position:
            food.respawn()
            self.grow()

    def grow(self):
        self.ate_food = True
        copy = self.body[-1]
        self.body.insert(-1, copy)

    def at_this_pos(self, position):
        for part in self.body:
            if part == position:
                return True
        return False


tile_size = 40
grid_width = 15
grid_height = 15
image_size = 40

window_width = grid_width * tile_size
window_height = grid_height * tile_size
title = "Snake"
window = pyglet.window.Window(window_width, window_height, title)

batch = pyglet.graphics.Batch()
background = pyglet.graphics.OrderedGroup(0)
foreground = pyglet.graphics.OrderedGroup(1)
snake_pic = pyglet.image.load('Graphics/Snake.png')
snake_grid = pyglet.image.ImageGrid(snake_pic, 4, 4)


@window.event
def on_draw():
    window.clear()
    snake.draw()


@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.LEFT:
        snake.change_dir(Vector2D(-1, 0))
    elif symbol == key.UP:
        snake.change_dir(Vector2D(0, 1))
    elif symbol == key.RIGHT:
        snake.change_dir(Vector2D(1, 0))
    elif symbol == key.DOWN:
        snake.change_dir(Vector2D(0, -1))


glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

pyglet.clock.schedule_interval(update, 0.2)
background_images = []

load_background()
snake = Snake()
food = Food()
pyglet.app.run()
