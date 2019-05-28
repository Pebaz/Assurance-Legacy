from random import randint, choice, shuffle
from PyQt4.Qt import *
from PyQt4.QtGui import QWidget
from soundmgr import SoundManager
from imgmgr import ImageManager
from player import Player, Lyrium_Ball
from world import World
from enemy import *
import os

class Game(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.t = QTimer()
        QObject.connect(self.t, SIGNAL('timeout()'), self, SLOT('repaint()'))
        self.t.start(17)
        self.setFixedSize(800, 600)
        self.setWindowTitle('Assurance')

        # Game Fields
        self.running = False
        self.state = 0
        self.image = ImageManager()
        self.sound = SoundManager()
        self.entities = []
        self.world = World(self)
        self.player = Player(self)
        self.player_score = 0
        self.player_best = 0
        self.letterhead = self.image.load_image('res/img/Letterhead2.png')
        self.deadhead = self.image.load_image('res/img/DeadHead.png')
        self.entity_queue = []
        self.wave_timer = 100

    def paintEvent(self, event):
        if self.running:
            painter = QPainter(self)
            painter.fillRect(0, 0, self.width(), self.height(),
                             QColor(55, 55, 55))

            if self.state == 0:
                self.world.render(painter)
                painter.fillRect(0, 0, self.width(), self.height(),
                                 QColor(0, 0, 0, 155))
                painter.drawImage(0, 64, self.letterhead)

            elif self.state == 1:
                self.update()
                self.render(painter)

            elif self.state == 2:
                self.world.render(painter)
                painter.fillRect(0, 0, self.width(), self.height(),
                                QColor(0, 0, 0, 155))
                painter.drawImage(0, 64, self.deadhead)
                painter.setFont(QFont("Hack", 20))
                painter.setPen(QColor(255, 155, 0))
                m = painter.fontMetrics()
                text = "Your score: " + str(self.player_score)
                x = self.width() / 2 - (m.width(text) / 2)
                y = self.height() / 2
                painter.drawText(x, y, text )

        else:
            #self.sound.stop()
            self.close()

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_Up or key == Qt.Key_W: self.player.mv_up = True
        if key == Qt.Key_Down or key == Qt.Key_S: self.player.mv_down = True
        if key == Qt.Key_Left or key == Qt.Key_A: self.player.mv_left = True
        if key == Qt.Key_Right or key == Qt.Key_D: self.player.mv_right = True
        if key == Qt.Key_Control: self.player.sprinting = True

    def keyReleaseEvent(self, event):
        key = event.key()

        if key == Qt.Key_Escape:
            self.running = False

        if key == Qt.Key_Space:
            self.state = 1
            self.reset_game()

        if key == Qt.Key_Up or key == Qt.Key_W: self.player.mv_up = False
        if key == Qt.Key_Down or key == Qt.Key_S: self.player.mv_down = False
        if key == Qt.Key_Left or key == Qt.Key_A: self.player.mv_left = False
        if key == Qt.Key_Right or key == Qt.Key_D: self.player.mv_right = False
        if key == Qt.Key_Control: self.player.sprinting = False

        if key == Qt.Key_Z: self.player.do_atk_light()
        if key == Qt.Key_X: self.player.do_atk_moder()
        if key == Qt.Key_C: self.player.do_atk_heavy()

    def start(self):
        self.running = True
        self.player.x = self.width() / 2
        self.player.y = self.height() / 2
        files = ['res/music/Two Steps - Archangel.mp3',
                 'res/music/Two Steps - Protectors of the Earth.mp3'
                 'res/music/Two Steps - Skyworld.mp3']
        files = ['res/music/Skyworld.wav', 'res/music/Archangel.wav']
        shuffle(files)
        self.sound.play_sound(files * 3)

    def update(self):
        self.sound.update()
        self.update_waves()
        self.player.update()

        for entity in self.entities:
            entity.update()
            if not entity.alive:
                self.entities.remove(entity)

        self.update_collisions()

        if not self.player.alive:
            self.state = 2

    def render(self, painter):
        self.world.render(painter)
        for entity in self.entities:
            entity.render(painter)

        self.player.render(painter)
        self.draw_health(painter)
        self.draw_score(painter)
        #self.DBG_draw_strikes(painter)

    def draw_health(self, painter):
        col = QColor(0, 155, 155, 155)
        painter.setPen(col)
        painter.drawRect(32, self.height()-32, self.width()-64, 32)
        col = QColor(255, 0, 55, 145)
        amnt = (self.player.current_hp / self.player.maximum_hp) *\
               self.width()-64
        painter.fillRect(32, self.height()-32, amnt, 32, col)

        amnt = (self.player.energy / 100) * self.width()-64
        painter.drawRect(32, self.height()-65, self.width()-64, 32)
        painter.fillRect(32, self.height()-65, amnt, 32, QColor(255,155,0,155))

    def draw_score(self, painter):
        painter.setPen(QColor(0, 0, 0))
        painter.setFont(QFont('Hack', 20))
        painter.drawText(0, 32, "Your Score: " + str(self.player_score))
        painter.drawText(0, 64, "Best Score: " + str(self.player_best))

    def DBG_draw_strikes(self, painter):
        for en in self.entities:
            painter.drawRect(en.get_bounds())

    def update_collisions(self):
        # Entity collisions
        for entity in self.entities:
            case = (isinstance(entity, Lyrium_Ball) or
                    isinstance(entity, Poison_Ball))
            if not case:

                bounds = entity.get_bounds()

                for other in self.entities:
                    if other is not entity and not isinstance(other, Poison_Ball):
                        other_bounds = other.get_bounds()

                        if bounds.intersects(other_bounds):
                            int_rect = bounds.intersected(other_bounds)

                            if int_rect.width() < int_rect.height():
                                if entity.x < other.x:
                                    entity.x = other.x - bounds.width()
                                else:
                                    entity.x = other.x + other_bounds.width()
                            else:
                                if entity.y < other.y:
                                    entity.y = other.y - bounds.height()
                                else:
                                    entity.y = other.y + other_bounds.height()

        x = self.player.x + self.player.get_bounds().width()
        if x > self.width():
            self.player.x = self.width() - self.player.get_bounds().width()
        if self.player.x < 0:
            self.player.x = 0
        y = self.player.y + self.player.get_bounds().height()
        if y > self.height():
            self.player.y = self.height() - self.player.get_bounds().height()
        if self.player.y < 0:
            self.player.y = 0

    def add_entity(self, entity):
        self.entities.append(entity)

    def update_waves(self):
        self.wave_timer -= 1
        if self.wave_timer <= 0:
            self.gen_wave()
            self.wave_timer = 100 * randint(4, 8)

    def gen_wave(self):
        spot1 = [3, 400]
        spot2 = [355, 32]
        spot3 = [746, 320]
        spot4 = [338, 557]
        spots = [spot1, spot2, spot3, spot4]

        for i in range(randint(1, 4)):
            spot = choice(spots)
            en = choice([Mush_Small(self), Mush_Ranged(self),
                         Mush_Radial(self), Mush_Muscle(self)])
            en.x = spot[0]
            en.y = spot[1]
            self.add_entity(en)

    def reset_game(self):
        if self.player_score > self.player_best:
            self.player_best = self.player_score
            self.player_score = 0
        self.entities.clear()
        self.player.x = self.width() / 2
        self.player.y = self.height() / 2
        self.player.reset()

