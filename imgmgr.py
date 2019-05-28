from PyQt4.Qt import *

class ImageManager:
    def __init__(self):
        self.images = {'null' : QImage('res/img/blank.png')}

    def load_image(self, filename, scale16=False):
        if filename in self.images:
            return self.images[filename]
        else:
            img = QImage(filename)
            if img.isNull():
                print('[Error] Couldn\'t find image: ' + filename)
                img = self.images['null']

            if scale16:
                tmp_imp = QImage(64, 64, QImage.Format_ARGB32)
                tmp_imp.fill(0x000000FF)
                gdd = QPainter(tmp_imp)
                gdd.scale(4, 4)
                gdd.drawImage(0, 0, img)
                gdd.end()
                img = tmp_imp
                
            self.images[filename] = img
            return img
                

