from PyQt4.Qt import *


class Entity:
    def __init__(self, gamed, x=0, y=0):
        self.game = gamed
        self.image = None
        self.x = y
        self.y = y
        self.current_hp = 100
        self.maximum_hp = 100
        self.alive = True

    def update(self):
        pass

    def render(self, painter):
        pass

    def hurt(self, damage):
        self.current_hp -= damage
        if self.current_hp <= 0:
            self.alive = False

    def get_bounds(self):
        return QRect(self.x, self.y, self.image.width(), self.image.height())
