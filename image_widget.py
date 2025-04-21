from PyQt6.QtCore import QByteArray, QRect
from PyQt6.QtGui import QImage, QPainter, QPainterPath, QPixmap
from PyQt6.QtWidgets import QWidget, QPushButton
from PyQt6.uic.properties import QtGui

from myimage import MyImage, defaultPhotoId


class ImageWidget(QPushButton):
    def __init__(self, imgId=defaultPhotoId, width=200, height=200, radius=100, parent=None):
        super().__init__(parent)
        self.image:QPixmap|None = None
        self.changeImageFromId(imgId)
        self.setFixedSize(width, height)
        self.radius = radius
        self.cachedPath = None
        self.updateCachedPath()

    def updateCachedPath(self):
        self.cachedPath = QPainterPath()
        self.cachedPath.addRoundedRect(0, 0, self.width(), self.height(), self.radius, self.radius)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateCachedPath()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setClipPath(self.cachedPath)
        rect = event.rect()
        painter.drawPixmap(rect, self.image)

    def changeImageFromId(self, imgId):
        self.image = MyImage(imgId).read().getQPixmap()
        self.update()

    def changeImageFromPath(self, path):
        self.image = QPixmap(path)
        self.update()

    def changeImageFromQPixmap(self, pixmap):
        self.image = pixmap
        self.update()


    # def paintEvent(self, event):
    #     painter = QPainter(self)
    #     painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    #     path = QPainterPath()
    #     path.addRoundedRect(0, 0, self.width(), self.height(), self.radius, self.radius)
    #     painter.setClipPath(path)
    #     rect = QRect(0, 0, self.width(), self.height())
    #     painter.drawImage(rect, self.image)
