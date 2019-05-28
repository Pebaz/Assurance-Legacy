class World:
    def __init__(self, game):
        self.game = game
        self.img = game.image.load_image('res/img/Map.png')

    def render(self, painter):
        painter.drawImage(0, 0, self.img)
