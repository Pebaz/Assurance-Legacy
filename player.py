import os
from PyQt4.Qt import *

from entity import Entity
from enemy import *

class Lyrium_Smoke(Entity):
    def __init__(self, gamed, x, y):
        self.alive = True
        self.x = x; self.y = y
        self.game = gamed
        self.image = self.game.image.load_image('res/img/Lyrium_Smoke.png', True)
        self.count = 40
    def render(self, painter):
        painter.drawImage(self.x, self.y, self.image)
    def update(self):
        self.y += 0.1
        self.count -= 1
        if self.count <= 0:
            self.alive = False
    def get_bounds(self):
        return QRect(-100, -100, 2, 2)

class Lyrium_Ball(Entity):
    def __init__(self, gamed, size, x, y, moves):
        Entity.__init__(self, gamed)
        self.x = x
        self.y = y
        self.hits = 1

        self.size = size
        if self.size == 1:
            self.offx = 24
            self.offy = 24
            self.b_size = 16
        elif self.size == 2:
            self.offx = 16
            self.offy = 16
            self.b_size = 32
        elif self.size == 3:
            self.offx = 8
            self.offy = 8
            self.b_size = 48
            self.hits = 3

        pre = 'res/img/'; post = '.png'
        imgs = [
            'Blank', 'Lyrium_Blast_Small', 'Lyrium_Blast_Medium', 'Lyrium_Blast_Large'
        ]
        imgs = [self.game.image.load_image(pre + i + post, True) for i in imgs]
        self.image = imgs[size]
        self.moves = moves
        self.speed = 6
        self.timer = 200
        self.damage = size * 25

    def render(self, painter):
        painter.drawImage(self.x, self.y, self.image)

    def update(self):
        moving = any(self.moves)

        if moving:
            if self.moves[0]: self.x -= self.speed
            elif self.moves[1]: self.x += self.speed
            if self.moves[2]: self.y -= self.speed
            elif self.moves[3]: self.y += self.speed
        else:
            self.y += self.speed

        for en in self.game.entities:
            if en is not self:
                if self.get_bounds().intersects(en.get_bounds()):
                    l = Lyrium_Smoke(self.game, en.x, en.y)
                    self.game.add_entity(l)

                    if not isinstance(en, Poison_Ball):
                        self.hits -= 1
                        if self.hits <= 0:
                            self.alive = False
                        en.hurt(self.damage)
                    else:
                        en.alive = False

        self.timer -= 1
        if self.timer <= 0: self.alive = False

    def get_bounds(self):
        return QRect(self.x+self.offx, self.y+self.offy,self.b_size,self.b_size)

class Player(Entity):
    def __init__(self, game):
        Entity.__init__(self, game)
        # Animation Fields:
        self.anim_atk_light = False
        self.anim_atk_moder = False
        self.anim_atk_heavy = False
        self.anim_atk_timer = 30
        self.image = self.game.image.load_image('res/img/Mushroom_Blue.png')
        self.images = [
            'res/img/Player_Root.png',
            'res/img/Player_Walk_1.png',
            'res/img/Player_Walk_2.png',
            'res/img/Player_Walk_Down_1.png',
            'res/img/Player_Walk_Down_2.png',
            'res/img/Player_Walk_Up_1.png',
            'res/img/Player_Walk_Up_2.png',
            'res/img/Player_Stk_Light_Wind.png',
            'res/img/Player_Stk_Light_Hit.png',
            'res/img/Player_Stk_Moder_Wind.png',
            'res/img/Player_Stk_Moder_Hit.png',
            'res/img/Player_Stk_Heavy_Wind.png',
            'res/img/Player_Stk_Heavy_Hit.png'
        ]
        self.images = [self.game.image.load_image(i, True) for i in self.images]
        self.image = self.images[0]
        self.mov_timer = 60

        # Movement fields
        self.mv_up = False
        self.mv_down = False
        self.mv_left = False
        self.mv_right = False
        self.speed = 4
        self.sprint = 6
        self.sprint_level = 30
        self.sprint_current = 30
        self.sprinting = False

        # Combat fields
        self.maximum_hp = 100
        self.current_hp = 100
        self.timer_atk_light = 12
        self.timer_atk_moder = 33
        self.timer_atk_heavy = 99
        self.atk_dir = []
        self.atk_light = False
        self.atk_moder = False
        self.atk_heavy = False
        self.energy = 100
        self.atk_light_cost = 10
        self.atk_moder_cost = 25
        self.atk_heavy_cost = 50

    def update(self):
        self.update_animations()
        self.update_health_and_energy()
        self.update_movement()
        self.update_attacks()

    def update_health_and_energy(self):
        self.energy += 0.1
        if self.energy > 100:
            self.energy = 100

        self.current_hp += 0.02
        if self.current_hp > self.maximum_hp:
            self.current_hp = self.maximum_hp
        if self.current_hp <= 0:
            self.alive = False

    def get_movement(self):
        return self.mv_left, self.mv_right, self.mv_up, self.mv_down

    def update_movement(self):
        speed = self.speed

        if any(self.get_movement()):
            self.atk_dir = self.get_movement()

        if self.sprinting and self.sprint_current > 0:
            self.sprint_current -= 1
            speed += self.sprint

        elif not self.sprinting:
            self.sprint_current += 1
            if self.sprint_current > self.sprint_level:
                self.sprint_current = self.sprint_level

        diag = self.mv_left or self.mv_right

        if self.mv_up and diag or self.mv_down and diag:
            if self.sprinting:
                tmp = speed - self.sprint
                speed = tmp / 2 + tmp / 4 + (self.sprint / 2 + self.sprint / 4)
            else:
                speed = speed / 2 + speed / 4

        if self.mv_up:    self.y -= speed; self.facing = 0
        if self.mv_down:  self.y += speed; self.facing = 2
        if self.mv_left:  self.x -= speed; self.facing = 3
        if self.mv_right: self.x += speed; self.facing = 1

    def update_attacks(self):
        attack_dir = False * 4
        if not any(self.get_movement()):
            attack_dir = self.atk_dir
        else:
            attack_dir = self.get_movement()

        if self.atk_light:
            if self.energy >= self.atk_light_cost:
                self.energy -= self.atk_light_cost
                # Spawn an energy ball
                self.game.add_entity(Lyrium_Ball(self.game, 1, self.x, self.y,
                                                 attack_dir))
                self.game.sound.play_sound('res/snd/fire4.wav')
            self.atk_light = False
            self.anim_atk = True


        if self.atk_moder:
            if self.energy >= self.atk_moder_cost:
                self.energy -= self.atk_moder_cost
                # Spawn an energy ball
                self.game.add_entity(Lyrium_Ball(self.game, 2, self.x, self.y,
                                                 attack_dir))
                self.game.sound.play_sound('res/snd/fire2.wav')

            self.atk_moder = False
            self.anim_atk = True

        if self.atk_heavy:
            if self.energy >= self.atk_heavy_cost:
                self.energy -= self.atk_heavy_cost
                # Spawn an energy ball
                self.game.add_entity(Lyrium_Ball(self.game, 3, self.x, self.y,
                                                 attack_dir))
                self.game.sound.play_sound('res/snd/fire3.wav')
            self.atk_heavy = False
            self.anim_atk = True

    def do_atk_light(self):
        self.atk_light = True

    def do_atk_moder(self):
        self.atk_moder = True

    def do_atk_heavy(self):
        self.atk_heavy = True

    def render(self, painter):
        painter.drawImage(self.x, self.y, self.image)
        painter.save()

        if self.sprinting or self.sprint_current < self.sprint_level:
            painter.setPen(QColor(255, 155, 55))
            painter.drawRect(self.x, self.y+64, 64, 3)
            amnt = (self.sprint_current / self.sprint_level) * 64
            painter.fillRect(self.x, self.y+64, amnt, 3, QColor(255, 155, 55))

        painter.restore()

    def get_bounds(self):
        return QRect(self.x+8, self.y, 48, 64)

    def update_animations(self):
        attacking = any([self.atk_light, self.atk_moder, self.atk_heavy])
        mov = any([self.mv_left, self.mv_right, self.mv_up, self.mv_down])
        recharging = not attacking and any([self.anim_atk_light,
                                            self.anim_atk_moder,
                                            self.anim_atk_heavy])
        self.anim_atk_timer -= 1
        if self.anim_atk_timer <= 0:
            self.anim_atk_timer = 30
            self.anim_atk_light = False
            self.anim_atk_moder = False
            self.anim_atk_heavy = False


        if attacking:
            if self.atk_light:
                self.image = self.images[7]

            if self.atk_moder:
                self.image = self.images[9]

            if self.atk_heavy:
                self.image = self.images[11]

        elif recharging:
            if self.anim_atk_light:
                self.image = self.images[8]
            elif self.anim_atk_moder:
                self.image = self.images[10]
            elif self.anim_atk_heavy:
                self.image = self.images[12]

        elif mov:
            self.mov_timer -= 1
            if self.mov_timer <= 0: self.mov_timer = 60
            upper_cycle = self.mov_timer <= 30

            if self.mv_down:
                if upper_cycle: self.image = self.images[3]
                else: self.image = self.images[4]

            if self.mv_up:
                if upper_cycle: self.image = self.images[5]
                else: self.image = self.images[6]

            if self.mv_left:
                if upper_cycle: self.image = self.images[1]
                else: self.image = self.image = self.images[2]

            if self.mv_right:
                if upper_cycle:
                    self.image = self.images[1].mirrored(True, False)
                else: self.image = self.images[2].mirrored(True, False)

        else:
            # Standing Still
            self.image = self.images[0]

    def reset(self):
        self.current_hp = self.maximum_hp
        self.atk_light = False
        self.atk_moder = False
        self.atk_heavy = False
        self.sprint_current = 30
        self.atk_dir = []
        self.alive = True
        self.energy = 100
