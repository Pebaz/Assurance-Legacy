from PyQt4.phonon import *
from PyQt4.Qt import *

class Sound:
    def __init__(self, file):
        self.finished = False
        self.output = Phonon.AudioOutput(Phonon.GameCategory)
        self.m_media = Phonon.MediaObject()
        Phonon.createPath(self.m_media, self.output)

        if isinstance(file, list):
            for i in file:
                self.m_media.enqueue(Phonon.MediaSource(i))
        else:
            self.m_media.setCurrentSource(Phonon.MediaSource(file))

        QObject.connect(self.m_media, SIGNAL('finished()'), self.done)

    def done(self, *args):
        self.finished = True

    def play(self):
        self.m_media.play()


class SoundManager:
    def __init__(self):
        self.sounds = []

    def play_sound(self, file):
        s = Sound(file)
        self.sounds.append(s)
        s.play()

    def update(self):
        '''
        for sound in self.sounds:
            if sound.m_media.remainingTime() <= 0:
                self.sounds.remove(sound)
        '''
        for sound in self.sounds:
            if sound.finished:
                self.sounds.remove(sound)

    def stop(self):
        for sound in self.sounds:
            sound.m_media.stop()

