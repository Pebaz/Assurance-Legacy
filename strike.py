from PyQt4.Qt import QRect

class Strike:
    def __init__(self, player, x, y):
        self.player = player
        self.x = x
        self.y = y
        self.active = True
        self.damage = 0

    def update(self):
        self.active = False

    def get_bounds(self):
        return QRect(self.x, self.y, 64, 64)

class Stk_Radial(Strike):
    pass

class Stk_Ranged(Strike):
    pass

class Lyrium_Strike(Strike):
    def __init__(self, player, x, y, size, movement):
        Strike.__init__(self, player, x, y)
        self.damage = size * 25
        self.x = x
        self.y = y
        self.counter = 300
        self.move = movement
        self.speed = 6
        self.size = size

    def render(self, painter):
        painter.drawImage(self.x, self.y, self.image)

    def update(self):
        speed = self.speed
        moving = any(self.move)
        movements = self.move
        
        # If moving left
        if movements[0]:
            self.x -= speed
            
        # if moving right
        elif movements[1]:
            self.x += speed

        # if moving up
        if movements[2]:
            self.y -= speed

        # if moving down
        elif movements[3]:
            self.y += speed

        if not moving:
            # Make the strike hit down
            if self.size < 3:
                self.y += speed
            elif self.size == 3:
                self.x += speed
            elif self.size == 4:
                self.x -= speed
                
        self.counter -= 1
        if self.counter <= 0:
            self.active = False

    def get_bounds(self):
        s = self.size * 16
        if s > 64: s -= 8
        x = self.x + (48 - s)
        y = self.y + (48 - s)
        return QRect(x, y, s, s)
        

class Stk_Light(Strike):
    def __init__(self, player, x, y, movements):
        Strike.__init__(self, player, x, y)
        self.damage = 20
        
        moving = movements[0] or movements[1] or movements[2] or movements[3]
        
        self.offx = 0
        self.offy = 0

        # If moving left
        if movements[0]:
            self.offx = -32
            self.offy = 16
            
        # if moving right
        elif movements[1]:
            self.offx = 64
            self.offy = 16

        # if moving up
        if movements[2]:
            self.offx = 16
            self.offy = -32

        # if moving down
        elif movements[3]:
            self.offx = 16
            self.offy = 64

        if not moving:
            # Make the strike hit down
            self.offx = 16
            self.offy = 64

    def get_bounds(self):
        return QRect(self.x+self.offx, self.y+self.offy, 16, 16)
    
class Stk_Moder(Strike):
    def __init__(self, player, x, y, movements):
        Strike.__init__(self, player, x, y)
        self.damage = 50
        moving = movements[0] or movements[1] or movements[2] or movements[3]

        self.offx = 0
        self.offy = 0

        # If moving left
        if movements[0]:
            self.offx = -32
            self.offy = 16
            
        # if moving right
        elif movements[1]:
            self.offx = 64
            self.offy = 16

        # if moving up
        if movements[2]:
            self.offx = 16
            self.offy = -32

        # if moving down
        elif movements[3]:
            self.offx = 16
            self.offy = 64

        if not moving:
            # Make the strike hit down
            self.offx = 16
            self.offy = 64

    def get_bounds(self):
        return QRect(self.x+self.offx, self.y+self.offy, 32, 32)

class Stk_Heavy(Strike):
    def __init__(self, player, x, y, movements):
        Strike.__init__(self, player, x, y)
        self.damage = 75
        self.width = 64
        self.offx = 0
        self.offy = 0

        moving = movements[0] or movements[1] or movements[2] or movements[3]

        # If moving left
        if movements[0]:
            self.offx = -64
            
        # if moving right
        elif movements[1]:
            self.offx = 64

        # if moving up
        if movements[2]:
            self.offy = -64

        # if moving down
        elif movements[3]:
            self.offy = 64

        if not moving:
            # Make the strike hit both left and right sides
            self.offx = -32
            self.offy = 0
            self.width = 128

    def get_bounds(self):
        return QRect(self.x + self.offx, self.y + self.offy, self.width, 64)
    
