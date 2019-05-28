from random import random, choice, randint
from PyQt4.Qt import *
from player import Entity
from PyQt4.phonon import *

class Splatter(Entity):
    def __init__(self, game, x, y):
        Entity.__init__(self, game)
        self.image = self.game.image.load_image('res/img/Splatter_Orange.png')
        self.count = 60
        self.x = x
        self.y = y
        self.current_hp = 10000

    def render(self, painter):
        painter.drawImage(self.x, self.y, self.image)

    def update(self):
        self.count -= 1
        if self.count <= 0:
            self.alive = False

    def get_bounds(self):
        return QRect(-100, -100 * random(), 2, 2)

class Poison_Ball(Entity):
    def __init__(self, game, x, y):
        Entity.__init__(self, game)
        self.image = self.game.image.load_image(
                'res/img/Poison_' + str(randint(1, 5)) + '.png', True)
        self.count = 1000
        self.x = x
        self.y = y
        self.damage = 15
        self.current_hp = 1000000
        self.bake = []
        self.speed = 4.0
        self.get_vector()

    def render(self, painter):
        painter.drawImage(self.x, self.y, self.image)

    def update(self):
        self.count -= 1
        if self.count <= 0:
            self.alive = False
        if self.get_bounds().intersects(self.game.player.get_bounds()):
            self.alive = False
            self.game.player.hurt(self.damage)
        self.seek_player()

    def get_vector(self):
        px = self.game.player.x
        py = self.game.player.y
        x = self.x
        y = self.y

        distx = abs(x - px)
        disty = abs(y - py)

        dist = distx + disty

        points = self.speed
        xpnts = (distx / dist) * points
        ypnts = (disty / dist) * points

        self.bake = [xpnts, ypnts]

        if x > px:
            self.bake[0] = -self.bake[0]

        if y > py:
            self.bake[1] = -self.bake[1]

    def seek_player(self):
        self.x += self.bake[0]
        self.y += self.bake[1]

    def get_bounds(self):
        return QRect(self.x+8, self.y+8, 48, 48)

class Mush_Small(Entity):
    def __init__(self, game):
        Entity.__init__(self, game)
        self.game = game
        self.image = self.game.image.load_image('res/img/Mushroom_Orange.png')
        s = 1
        if choice([True, False]): s += random()
        else: s -= random()
        self.speed = s
        self.threshhold = 0#random() * 64
        self.m_range = 180
        self.current_hp = 60
        self.maximum_hp = 60

    def hurt(self, damage):
        self.current_hp -= damage
        if self.current_hp <= 0:
            self.alive = False
            self.game.add_entity(Splatter(self.game, self.x, self.y))

            self.game.sound.play_sound('res/snd/goosh.wav')
            self.game.player_score += 1

    def update(self):
        self.seek_player()
        if self.get_bounds().intersects(self.game.player.get_bounds()):
            self.game.player.hurt(25)
            self.game.sound.play_sound('res/snd/explosion.wav')
            self.hurt(self.maximum_hp)

    def seek_player(self):
        player = self.game.player

        on_left = player.x + self.threshhold < self.x
        on_right = player.x - self.threshhold > self.x
        above = player.y + self.threshhold < self.y
        below = player.y - self.threshhold > self.y
        moving = player.mv_left or player.mv_right or player.mv_up \
                 or player.mv_down
        mv_left = player.mv_left
        mv_right = player.mv_right
        mv_up = player.mv_up
        mv_down = player.mv_down

        in_rangex = (on_right and player.x < self.x + self.m_range) or\
                    (on_left and player.x > self.x - self.m_range)

        in_rangey = (below and player.y < self.y + self.m_range) or\
                    (above and player.y > self.y - self.m_range)

        in_range = in_rangex and in_rangey

        if not in_range:
            if on_left and (above or below) and mv_down:
                self.y += self.speed
                self.x -= self.speed

            elif on_left and (above or below) and mv_up:
                self.y -= self.speed
                self.x -= self.speed

            elif on_right and (above or below) and mv_down:
                self.y += self.speed
                self.x += self.speed

            elif on_left and (above or below) and mv_up:
                self.y -= self.speed
                self.x += self.speed
            else:
                in_range = True

        if in_range:
            if on_left:
                self.x -= self.speed
            elif on_right:
                self.x += self.speed

            if above:
                self.y -= self.speed
            elif below:
                self.y += self.speed

    def render(self, painter):
        painter.drawImage(self.x, self.y, self.image)
        self.render_health(painter)

    def render_health(self, painter):
        painter.setPen(QColor(255, 0, 55))
        painter.drawRect(self.x, self.y+64, 64, 3)
        amnt = (self.current_hp / self.maximum_hp) * 64
        painter.fillRect(self.x, self.y+64, amnt, 3, QColor(255, 0, 55))

    def get_bounds(self):
        return QRect(self.x+8, self.y+8, 48, 48)

class Mush_Ranged(Entity):
    def __init__(self, game, x=0, y=0):
        self.game = game
        self.x = x
        self.y = y
        self.current_hp = 30
        self.maximum_hp = 30
        self.alive = True
        imgs = ['res/img/Mushroom_REd.png', 'res/img/Mush_Ranged.png']
        self.imgs = [game.image.load_image(i) for i in imgs]
        self.image = self.imgs[0]
        self.speed = 0.5 + random()

        # Atk Commands
        self.atk_range = 64 + 64 * random()
        self.atk_timer = 60
        self.atk_tick = 60
        self.attacking = False
        self.recharging = False

    def render_health(self, painter):
        painter.setPen(QColor(255, 0, 55))
        painter.drawRect(self.x, self.y+64, 64, 3)
        amnt = (self.current_hp / self.maximum_hp) * 64
        painter.fillRect(self.x, self.y+64, amnt, 3, QColor(255, 0, 55))

    def render(self, painter):
        painter.drawImage(self.x, self.y, self.image)
        self.render_health(painter)
        #painter.drawRect(self.get_bounds())
        #painter.drawRect(self.get_range())
        #amnt = 64 * (self.atk_tick / self.atk_timer)
        #painter.drawRect(self.x, self.y+64, amnt, 3)

    def update(self):
        p = self.game.player
        s = self.speed

        if p.get_bounds().intersects(self.get_range()):
            # In Range, fire shot
            if self.atk_tick == self.atk_timer:
                self.game.add_entity(Poison_Ball(self.game, self.x, self.y))
                self.game.sound.play_sound('res/snd/goosh2.wav')
                self.attacking = True
        else:
            if self.x < p.x:
                self.x += s
            elif self.x > p.x:
                self.x -= s

            if self.y < p.y:
                self.y += s
            elif self.y > p.y:
                self.y -= s

        if self.get_bounds().intersects(self.game.player.get_bounds()):
            self.game.player.hurt(25)
            self.game.add_entity(Splatter(self.game, self.x, self.y))
            self.game.sound.play_sound('res/snd/explosion.wav')
            self.alive = False

        self.update_animations()

    def get_bounds(self):
        return QRect(self.x+8, self.y+8, 48, 48)

    def get_range(self):
        _2 = self.atk_range * 2 + 64
        return QRect(self.x-self.atk_range, self.y-self.atk_range, _2, _2)

    def update_animations(self):
        if self.attacking:
            self.atk_tick -= 1

        elif self.recharging:
            self.atk_tick += 1

        if self.atk_tick > self.atk_timer:
            self.atk_tick = self.atk_timer
            self.recharging = False

        elif self.atk_tick <= 0:
            self.attacking = False
            self.recharging = True

        if self.attacking and self.atk_tick < self.atk_timer:
            self.image = self.imgs[1]

        elif self.recharging and self.atk_tick < self.atk_timer:
            self.image = self.imgs[0]

    def hurt(self, damage):
        self.current_hp -= damage
        if self.current_hp <= 0:
            self.alive = False
            self.game.add_entity(Splatter(self.game, self.x, self.y))
            self.game.player_score += 1
            self.game.sound.play_sound('res/snd/goosh.wav')

class Mush_Radial(Entity):
    def __init__(self, game, x=0, y=0):
        self.game = game
        self.x = x
        self.y = y
        self.current_hp = 25
        self.maximum_hp = 25
        self.alive = True
        imgs = ['res/img/Mushroom_Green.png', 'res/img/Mush_Radial.png',
                'res/img/Poison_Radial_1.png', 'res/img/Poison_Radial_2.png',
                'res/img/Poison_Radial_3.png']
        self.imgs = [game.image.load_image(i) for i in imgs]
        self.image = self.imgs[0]
        self.radius = self.imgs[2]
        self.speed = 0.5 + random()

        # Atk Commands
        self.variance = random()
        self.atk_range = 64
        self.atk_timer = 120
        self.atk_tick = 120
        self.attacking = False
        self.recharging = False
        self.atk_pos = [0, 0]

    def render_health(self, painter):
        painter.setPen(QColor(255, 0, 55))
        painter.drawRect(self.x, self.y+64, 64, 3)
        amnt = (self.current_hp / self.maximum_hp) * 64
        painter.fillRect(self.x, self.y+64, amnt, 3, QColor(255, 0, 55))

    def render(self, painter):
        if self.attacking:
            x = self.atk_pos[0]; y = self.atk_pos[1]
            w = self.radius.width()
            if self.radius == self.imgs[2]:
                painter.drawImage(x, y, self.radius)
            elif self.radius == self.imgs[3]:
                painter.drawImage(x - w / 4, y - w / 4, self.radius)
            elif self.radius == self.imgs[4]:
                painter.drawImage(x - w / 4, y - w / 4, self.radius)

        painter.drawImage(self.x, self.y, self.image)
        self.render_health(painter)

        '''
        # Draw the bounding box
        painter.drawRect(self.get_bounds())

        # Draw how far away the shroom has to be before it attacks
        painter.setPen(QColor(255, 0, 55))
        painter.drawRect(self.get_range())

        # Draw the radius of the current attack
        painter.setPen(QColor(255, 255, 0))
        painter.drawRect(self.get_atk_radius())

        # Draw the atk_bar
        amnt = 64 * (self.atk_tick / self.atk_timer)
        painter.setPen(QColor(55, 155, 55))
        painter.drawRect(self.x, self.y+64, amnt, 3)
        '''

    def update(self):
        p = self.game.player
        s = self.speed

        if p.get_bounds().intersects(self.get_range()):
            # In Range, fire radial poison attack
            if self.atk_tick == self.atk_timer:
                #self.game.add_entity(Poison_Ball(self.game, self.x, self.y))
                self.attacking = True
                self.atk_pos = [self.x, self.y]
                self.game.sound.play_sound('res/snd/smoosh.wav')
        else:
            if self.x < p.x:
                self.x += s
            elif self.x > p.x:
                self.x -= s

            if self.y < p.y:
                self.y += s
            elif self.y > p.y:
                self.y -= s

        if self.get_bounds().intersects(self.game.player.get_bounds()):
            self.game.player.hurt(25)
            self.game.add_entity(Splatter(self.game, self.x, self.y))
            self.hurt(self.maximum_hp)
            self.game.sound.play_sound('res/snd/explosion.wav')
        elif self.get_atk_radius().intersects(self.game.player.get_bounds()):
            self.game.player.hurt(0.2)

        self.update_animations()

    def get_bounds(self):
        return QRect(self.x+8, self.y+8, 48, 48)

    def get_range(self):
        w = self.atk_range
        return QRect(self.x - w, self.y - w, w * 2 + 64, w * 2 + 64)

    def get_atk_radius(self):
        if self.attacking:
            if not self.radius == self.imgs[2]:
                w = self.radius.width()
                return QRect(self.atk_pos[0] - w / 4, self.atk_pos[1] - w / 4, w, w)
            else:
                return QRect(self.atk_pos[0], self.atk_pos[1], 64, 64)
        else:
            return QRect(0, 0, 0, 0)

    def update_animations(self):
        if self.attacking:
            self.atk_tick -= 1

        elif self.recharging:
            self.atk_tick += 1

        if self.atk_tick > self.atk_timer:
            self.atk_tick = self.atk_timer
            self.recharging = False

        elif self.atk_tick <= 0:
            self.attacking = False
            self.recharging = True

        if self.attacking and self.atk_tick < self.atk_timer:
            t = self.atk_tick
            tm = self.atk_timer
            p25 = tm / 4
            p50 = tm / 2
            p75 = tm - p25

            if t > p75 and t < tm:  # 25% done with atk
                self.radius = self.imgs[2]
            elif t > p50 and t < p75:  # 50% done with atk
                self.radius = self.imgs[3]
            elif t > p25 and t < p50:  # 75% done with atk
                self.radius = self.imgs[4]

            self.image = self.imgs[1]

        elif self.recharging and self.atk_tick < self.atk_timer:
            self.image = self.imgs[0]

    def hurt(self, damage):
        self.current_hp -= damage
        if self.current_hp <= 0:
            self.alive = False
            self.game.add_entity(Splatter(self.game, self.x, self.y))
            self.game.player_score += 1
            self.game.sound.play_sound('res/snd/goosh.wav')

class Mush_Muscle(Entity):
    def __init__(self, game, x=0, y=0):
        self.game = game
        self.x = x
        self.y = y
        self.current_hp = 300
        self.maximum_hp = 300
        self.alive = True
        imgs = ['res/img/Mush_Muscle.png', 'res/img/Hand.png',
                'res/img/Smoke_1.png']
        self.imgs = [game.image.load_image(i) for i in imgs]
        self.image = self.imgs[0]
        self.hand_l = self.imgs[1]
        self.hand_r = self.imgs[1].mirrored(True, False)
        self.smoke = self.imgs[2]

        self.speed = 0.2 + (random() / 2.0)

        # Atk Commands
        self.atk_range = 64 + 64 * random()
        self.atk_timer = 60
        self.atk_tick = 60
        self.attacking = False
        self.recharging = False

        self.boom_gen = False
        self.booming = False
        self.boom_pos = [0, 0]
        self.boom_radius = 0
        self.boom_rect = QRect()

    def render_health(self, painter):
        painter.setPen(QColor(255, 0, 55))
        painter.drawRect(self.x, self.y+128, 128, 3)
        amnt = (self.current_hp / self.maximum_hp) * 128
        painter.fillRect(self.x, self.y+128, amnt, 3, QColor(255, 0, 55))

    def render(self, painter):
        if self.booming:
            painter.save()

            x = self.boom_rect.x(); y = self.boom_rect.y()
            w = self.boom_rect.width(); h = self.boom_rect.height()
            scl = (w / 16.0)
            painter.translate(x-x/8, y-y/8)
            painter.scale(scl+scl/8, scl+scl/8)
            painter.drawImage(0, 0, self.smoke)
            painter.restore()

        painter.drawImage(self.x, self.y, self.image)

        dly = 64 - ((self.atk_tick / self.atk_timer) * 64)
        painter.drawImage(self.x - 16, (self.y+64)-dly, self.hand_l)

        dry = 64 - ((self.atk_tick / self.atk_timer) * 64)
        painter.drawImage(self.x + 76, (self.y+64)-dry, self.hand_r)

        #painter.setPen(QColor(255, 255, 0))
        #painter.drawRect(self.get_bounds())

        self.render_health(painter)

    def update(self):
        p = self.game.player
        s = self.speed

        if p.get_bounds().intersects(self.get_range()):
            # In Range, fire shot
            if self.atk_tick == self.atk_timer:
                self.attacking = True
        else:
            if self.x < p.x:
                self.x += s
            elif self.x > p.x:
                self.x -= s

            if self.y < p.y:
                self.y += s
            elif self.y > p.y:
                self.y -= s

        if self.get_bounds().intersects(self.game.player.get_bounds()):
            self.game.player.hurt(1)
            self.game.add_entity(Splatter(self.game, self.x, self.y))
            self.hurt(0.01)

        self.update_animations()

        if self.boom_gen:
            self.boom_gen = False
            self.boom_pos = [self.x+64, self.y+64]
            self.booming = True
            self.game.sound.play_sound('res/snd/boom.wav')

        if self.booming:
            self.boom_radius += 4
            if self.boom_radius > 200:
                self.booming = False
                self.boom_rect = QRect()
                self.boom_radius = 0
            r = self.boom_radius
            self.boom_rect = QRect(self.boom_pos[0]-r, self.boom_pos[1]-r,
                           r*2, r*2)

        if self.boom_rect.intersects(self.game.player.get_bounds()):
            self.game.player.hurt(2)

    def get_bounds(self):
        return QRect(self.x+32, self.y+32, 64, 64)

    def get_range(self):
        _2 = self.atk_range * 2 + 64
        return QRect(self.x-self.atk_range, self.y-self.atk_range, _2, _2)

    def update_animations(self):
        # Handle ticking
        if self.attacking:
            self.atk_tick -= 1
        elif self.recharging:
            self.atk_tick += 4
        if self.atk_tick >= self.atk_timer:
            self.atk_tick = self.atk_timer
            if self.recharging:
                self.boom_gen = True
            self.recharging = False

        elif self.atk_tick <= 0:
            self.attacking = False
            self.recharging = True
            #self.game.add_entity(Poison_Ball(self.game, self.x, self.y))
            # Ground Pound!

    def hurt(self, damage):
        self.current_hp -= damage
        if self.current_hp <= 0:
            self.alive = False

            for i in range(4):
                r = random() * 2
                s = Splatter(self.game, self.x - r, self.y - r)
                self.game.add_entity(s)

                r = random() * 64
                s = Splatter(self.game, self.x + r, self.y + r)
                self.game.add_entity(s)
            self.game.player_score += 1
