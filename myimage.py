import base64

from PyQt6.QtCore import QByteArray
from PyQt6.QtGui import QImage, QPixmap, QIcon

import remote

defaultPhotoId = 0
defaultCoverId = 1
addGoodsIconId = 2

class MyImage:
    nextId = 0
    def __init__(self, _id = None):
        self.id = _id
        self.data = None

    @staticmethod
    def init():
        result = remote.get_max_id("image")
        if result is not None:
            MyImage.nextId = result + 1
        else:
            exit(-1)

        if MyImage.nextId == defaultPhotoId:
            image = MyImage()
            image.allocId()
            image.openAt("./default_profile_photo.png")
            image.insert()
        if MyImage.nextId == defaultCoverId:
            image = MyImage()
            image.allocId()
            image.openAt("./default_cover.png")
            image.insert()
        if MyImage.nextId == addGoodsIconId:
            image = MyImage()
            image.allocId()
            image.openAt("./add_goods.jpg")
            image.insert()

    def allocId(self):
        self.id = MyImage.nextId
        MyImage.nextId += 1

    def insert(self):
        remote.insert_image(self.id, self.data)

    def read(self):
        result = remote.get_image(self.id)
        if result is not None:
            self.data = result
        return self

    def write(self):
        remote.set_image(self.id, self.data)
        
    def openAt(self, fileName):
        file = open(fileName, "rb")
        self.data = file.read()
        file.close()

    def getUrl(self):
        return "data:image/png;base64,%s" % base64.b64encode(self.data).decode('utf-8')

    def getQPixmap(self) -> QPixmap:
        return QPixmap().fromImage(self.getQImage())

    def getQIcon(self) -> QIcon:
        return QIcon(self.getQPixmap())

    def getQImage(self) -> QImage:
        return QImage.fromData(QByteArray(self.data))
