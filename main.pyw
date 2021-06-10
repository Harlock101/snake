import random
import pyglet
from pyglet.window import key
from pyglet.gl import *


def load_background():
    for y in range(grid_height):
        for x in range(grid_width):
            sprite = pyglet.sprite.Sprite(snake_grid[(0, 3)], x * tile_size, y * tile_size, batch=batch, group=back)
            sprite.scale = tile_size / image_size
            background.append(sprite)


def update(dt):
    snake.update()


def game_over():
    print("Game over")
    exit(666)


class FOOD:
    def __init__(self):
        self.apple = pyglet.sprite.Sprite(snake_grid[(0, 2)], batch=batch, group=fore)
        self.apple.scale = tile_size / image_size
        self.x = 0
        self.y = 0
        self.respawn()

    def respawn(self):
        while True:
            self.x = random.randint(0, grid_width - 1)
            self.y = random.randint(0, grid_height - 1)
            if not snake.at_this_pos(self.x, self.y):
                break
        self.apple.x = self.x * tile_size
        self.apple.y = self.y * tile_size


class SNAKE:
    def __init__(self):
        self.body = [(3, 0), (2, 0), (1, 0), (0, 0)]
        self.direction = (1, 0)
        self.new_direction = (1, 0)
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

        self.body_tail = {
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
        for index, tail in enumerate(self.body):
            if index == 0:
                img = pyglet.sprite.Sprite(self.head[self.direction], tail[0] * tile_size, tail[1] * tile_size,
                                           batch=batch, group=fore)
            elif index == len(self.body) - 1:
                tail_dir = (self.body[index-1][0] - tail[0], self.body[index-1][1] - tail[1])
                if tail_dir == (0, 0):
                    tail_dir = (self.body[index - 2][0] - self.body[index-1][0],
                                self.body[index - 2][1] - self.body[index-1][1])
                img = pyglet.sprite.Sprite(self.tail[tail_dir],
                                           tail[0] * tile_size, tail[1] * tile_size, batch=batch, group=fore)
            else:
                if self.ate_food and index == len(self.body) - 2:
                    continue
                if tail[0] == self.body[index-1][0]:
                    body_dir = (self.body[index - 1][0] - self.body[index + 1][0],
                                self.body[index - 1][1] - self.body[index + 1][1])
                else:
                    body_dir = (self.body[index + 1][0] - self.body[index - 1][0],
                                self.body[index + 1][1] - self.body[index - 1][1])
                img = pyglet.sprite.Sprite(self.body_tail[body_dir], tail[0] * tile_size, tail[1] * tile_size,
                                           batch=batch, group=fore)
            img.scale = tile_size / image_size
            images.append(img)
        batch.draw()

    def update(self):
        self.ate_food = False
        self.direction = self.new_direction
        x_pos = self.body[0][0] + self.direction[0]
        y_pos = self.body[0][1] + self.direction[1]
        self.body.insert(0, (x_pos, y_pos))
        del self.body[-1]
        self.check_collision()

    def change_dir(self, direct):
        if self.direction[0] + direct[0] != 0 or self.direction[1] + direct[1] != 0:
            self.new_direction = direct

    def check_collision(self):
        if self.body[0][0] < 0 or self.body[0][0] > grid_width - 1 \
                or self.body[0][1] < 0 or self.body[0][1] > grid_height - 1:
            game_over()
        for part in self.body[1:]:
            if part[0] == self.body[0][0] and part[1] == self.body[0][1]:
                game_over()
        if self.body[0][0] == food.x and self.body[0][1] == food.y:
            food.respawn()
            self.grow()

    def grow(self):
        self.ate_food = True
        copy = self.body[-1]
        self.body.insert(-1, copy)

    def at_this_pos(self, x, y):
        for part in self.body:
            if part[0] == x and part[1] == y:
                return True
        return False


tile_size = 40
grid_width = 20
grid_height = 20
image_size = 40

window_width = grid_width * tile_size
window_height = grid_height * tile_size
title = "Snake"

window = pyglet.window.Window(window_width, window_height, title)
batch = pyglet.graphics.Batch()
back = pyglet.graphics.OrderedGroup(0)
fore = pyglet.graphics.OrderedGroup(1)
snake_pic = pyglet.image.load('Graphics/Snake.png')
snake_grid = pyglet.image.ImageGrid(snake_pic, 4, 4)
background = []
load_background()
snake = SNAKE()
food = FOOD()


@window.event
def on_draw():
    window.clear()
    snake.draw()


@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.LEFT:
        snake.change_dir((-1, 0))
    elif symbol == key.UP:
        snake.change_dir((0, 1))
    elif symbol == key.RIGHT:
        snake.change_dir((1, 0))
    elif symbol == key.DOWN:
        snake.change_dir((0, -1))


glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

pyglet.clock.schedule_interval(update, 0.2)
pyglet.app.run()
