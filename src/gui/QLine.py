from PyQt5.QtWidgets import QFrame

class QLine(QFrame):

    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
