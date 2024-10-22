from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QDialog, QLabel, QVBoxLayout, QGridLayout, QPushButton, QHBoxLayout, QSpacerItem, \
    QSizePolicy, QMessageBox

from goods import Goods
from user import User


class GoodsDetailsUi(QDialog):
    exited = pyqtSignal()
    def __init__(self, parent, gid, _user):
        super().__init__(parent)
        self.user = _user
        self.goods = Goods(gid)
        self.goods.read()

        self.setWindowTitle("商品详情")
        self.setFixedSize(800, 600)

        self.textArea = QLabel(self)
        self.textArea.setTextFormat(Qt.TextFormat.RichText)
        self.textArea.setText(f'''
            <h1 style="color:black;">{self.goods.name}<h1>
            <p style="color:red;">¥{"%0.2f"%self.goods.price}</p>
            <p style="font-size:18px;">{self.goods.description}</p>
        ''')

        self.bottomArea = QWidget(self)

        self.commentBtn = QPushButton("评论", self)
        self.collectBtn = QPushButton("收藏", self)
        self.messageBtn = QPushButton("联系卖家", self)
        self.purchaseBtn = QPushButton("购买", self)
        self.purchaseBtn.clicked.connect(lambda: self.purchase())

        textAreaLayout = QHBoxLayout()
        textAreaLayout.addWidget(self.commentBtn)
        textAreaLayout.addWidget(self.collectBtn)
        textAreaLayout.addSpacing(600)
        textAreaLayout.addWidget(self.messageBtn)
        textAreaLayout.addWidget(self.purchaseBtn)
        self.bottomArea.setLayout(textAreaLayout)

        generalLayout = QVBoxLayout()
        generalLayout.addWidget(self.textArea)
        generalLayout.addSpacerItem(QSpacerItem(self.width(), 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        generalLayout.addWidget(self.bottomArea)

        self.setLayout(generalLayout)

    def purchase(self):
        if self.user.purchase(self.goods.id):
            QMessageBox.information(self, "购买成功", "下单成功, 等待卖家发货.")
            self.close()
        else:
            QMessageBox.critical(self, "购买失败", "下单失败.")

    def closeEvent(self, event):
        self.exited.emit()
        QDialog.closeEvent(self, event)


class UserDetailsUi(QDialog):
    def __init__(self, uid, parent):
        super().__init__(parent)
        self.user = User(uid)
        self.user.read()
        self.setFixedSize(200, 150)

        self.chatBtn = QPushButton("聊天", self)

