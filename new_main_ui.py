import random

from PyQt6.QtCore import Qt, QSize, pyqtSlot, QTimer
from PyQt6.QtGui import QPalette, QStandardItemModel
from PyQt6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QApplication, QHBoxLayout, QGridLayout, QLineEdit, \
    QPushButton, QGroupBox, QVBoxLayout, QScrollArea, QLabel, QAbstractItemView, QSpacerItem, QSizePolicy, QFileDialog, \
    QTableWidget, QTableView, QHeaderView

from chat import Chat
from details_ui import GoodsDetailsUi, UserDetailsUi
from goods import Goods
from image_widget import ImageWidget
from myimage import MyImage
from user import User


class NewMainUi(QWidget):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.setFixedSize(1366, 768)
        self.user = user
        self.pageSideBar = QListWidget(self)
        self.pageSideBar.setFixedWidth(60)
        self.pages = {
            "首页": HomePage(self),
            "消息": MessagePage(self),
            "我的": MyProfilePage(self),
        }

        for name in self.pages.keys():
            item = QListWidgetItem(name)
            self.pageSideBar.addItem(item)
            self.pages[name].hide()
        self.pageSideBar.currentItemChanged.connect(self.changePage)

        generalLayout = QHBoxLayout()
        generalLayout.setContentsMargins(0, 0, 0, 0)
        generalLayout.setSpacing(0)
        generalLayout.addWidget(self.pageSideBar)
        for page in self.pages.values():
            generalLayout.addWidget(page)
        self.setLayout(generalLayout)

    def changePage(self, currentPage:QListWidgetItem, previousPage:QListWidgetItem):
        if previousPage is not None:
            self.pages[previousPage.text()].hide()
        self.pages[currentPage.text()].show()

class HomePage(QWidget):
    def __init__(self, parent: NewMainUi):
        super().__init__(parent)
        self.user = parent.user
        #顶部搜索框
        searchBox = QLineEdit(self)
        searchBox.setPlaceholderText("输入商品名或用户名搜索")
        searchButton = QPushButton("搜索")
        searchButton.clicked.connect(lambda: self.searchFor(searchBox.text()))

        searchLayout = QHBoxLayout()
        searchLayout.addWidget(searchBox)
        searchLayout.addWidget(searchButton)

        #商品展示区
        self.goodsList = GoodsList(self)
        goodsIdList = Goods.getOnSaleIdList(self.user.id)
        onSaleGoodsNum = len(goodsIdList)

        for i in range(onSaleGoodsNum):
            goodsWidget = self.createGoodsWidget(self.goodsList, goodsIdList[i][0], goodsIdList[i][1])
            self.goodsList.addUnit(goodsWidget)
        self.goodsList.setRow(5)

        generalLayout = QVBoxLayout()
        generalLayout.addLayout(searchLayout)
        generalLayout.addWidget(self.goodsList)
        self.setLayout(generalLayout)

    def createGoodsWidget(self, parent, uid, gid) -> QWidget:
        goodsWidget = QWidget(parent)
        # print(self.homeGoodsContainer.width(), self.homeGoodsContainer.height())
        goodsWidget.setFixedSize(290, 160)
        colorRange = range(5, 250)
        backgroundColor = (random.choice(colorRange), random.choice(colorRange), random.choice(colorRange))
        userAreaColor = (255 - backgroundColor[0], 255 - backgroundColor[1], 255 - backgroundColor[2])
        goodsWidget.setStyleSheet(f'''
            QWidget {{
                background-color: rgb{backgroundColor};
                padding: 2px;
                margin: 4px;
                border-radius: 8px;
            }}
        ''')
        goods = Goods(gid)
        goods.read()
        goodsCover = ImageWidget(goods.cid, 140, 140, 15, goodsWidget)
        goodsCover.clicked.connect(lambda: self.showGoodsDetail(gid))
        goodsTitle = QLabel(f"{goods.name}", goodsWidget)
        goodsTitle.setStyleSheet("background-color: rgb(255,255,255);")
        priceLabel = QLabel("¥%0.2f"%goods.price, goodsWidget)
        priceLabel.setStyleSheet("background-color: rgb(255,255,255);")
        pricePalette = QPalette()
        pricePalette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.red)
        priceLabel.setPalette(pricePalette)

        user = User(uid)
        user.read()
        userArea = QWidget(goodsWidget)
        userArea.setStyleSheet(f"background-color: rgb{userAreaColor};")
        unameLabel = QLabel(f"{user.nickname}", userArea)
        unameLabel.setStyleSheet(f'''
            QLabel{{
                background-color: rgb(255,255,255);
                color: rgb(0,0,0);
            }}
        ''')
        uhead = ImageWidget(user.hid, 30, 30, 15, userArea)
        uhead.clicked.connect(lambda: self.showUserDetail(user.id))

        userAreaLayout = QHBoxLayout()
        userAreaLayout.addWidget(unameLabel)
        userAreaLayout.addWidget(uhead)
        userArea.setLayout(userAreaLayout)

        layout = QGridLayout()
        layout.addWidget(goodsCover, 0, 0, 3, 1)
        layout.addWidget(goodsTitle, 0, 1)
        layout.addWidget(priceLabel, 1, 1)
        layout.addWidget(userArea, 2, 1)
        goodsWidget.setLayout(layout)

        return goodsWidget

    def showGoodsDetail(self, gid):
        detailsUi = GoodsDetailsUi(self, gid, self.user)
        # detailsUi.exited.connect(lambda: self.refreshGoodsArea())
        goods = Goods(gid)
        goods.read()
        # detailsUi.messageBtn.clicked.connect(lambda: self.chatWith(goods.uid, detailsUi))
        detailsUi.setModal(True)
        detailsUi.show()

    def showUserDetail(self, uid):
        detailsUi = UserDetailsUi(uid, self)
        # detailsUi.chatBtn.clicked.connect(lambda: self.chatWith(uid, detailsUi))
        detailsUi.setModal(True)
        detailsUi.show()


    def searchFor(self, keyword:str):
        print(keyword)

class MessagePage(QWidget):
    def __init__(self, parent: NewMainUi):
        super().__init__(parent)
        self.user = parent.user

        self.contactsList = ContactList(self)
        self.contactsList.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.contactsList.setMinimumWidth(200)
        self.contactsList.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.contactsList.setIconSize(QSize(50, 50))

        self.chatTitle = QLabel(self)
        self.chatTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chatMessageList = ChatMessageList(self)
        self.messageEditor = MessageEditor(self)
        self.chatWidget = QWidget(self)
        chatWidgetLayout = QVBoxLayout()
        chatWidgetLayout.addWidget(self.chatTitle)
        chatWidgetLayout.addWidget(self.chatMessageList)
        chatWidgetLayout.addWidget(self.messageEditor)
        self.chatWidget.setLayout(chatWidgetLayout)
        self.chatWidget.setFixedWidth(1100)
        self.chatWidget.hide()

        generalLayout = QHBoxLayout()
        generalLayout.addWidget(self.contactsList)
        generalLayout.addWidget(self.chatWidget)
        self.setLayout(generalLayout)

        self.contactsList.currentItemChanged.connect(self.openChat)
        self.messageEditor.sendButton.clicked.connect(lambda: self.sendMessage("text"))
        self.messageEditor.picButton.clicked.connect(lambda: self.sendMessage("image"))

    def openChat(self, currentChat:QListWidgetItem, previousChat:QListWidgetItem):
        uid = currentChat.data(Qt.ItemDataRole.UserRole)
        self.chatTitle.setText(currentChat.text())
        self.chatMessageList.refresh(uid)
        self.messageEditor.textEdit.clear()
        self.chatWidget.show()

    def sendMessage(self, _type="text"):
        if self.contactsList.currentItem() is None:
            return
        uid = self.contactsList.currentItem().data(Qt.ItemDataRole.UserRole)
        chat = Chat(self.user.id, uid)
        if _type == "text":
            content = self.messageEditor.textEdit.text()
            if len(content) < 1:
                return
            self.messageEditor.textEdit.clear()
            chat.insert(content, _type)
            self.chatMessageList.addMessage((self.user.id, content, _type, None))
        elif _type == "image":
            fileName, _ = QFileDialog.getOpenFileName(None, "选择图片", "", "Images (*.png *.xpm *.jpg)")
            print(fileName)
            if len(fileName) > 0:
                img = MyImage()
                img.openAt(fileName)
                img.allocId()
                img.insert()
                chat.insert(str(img.id), _type)
                print(img.id)
                self.chatMessageList.addMessage((self.user.id, str(img.id), _type, None))

class MyProfilePage(QWidget):
    def __init__(self, parent: NewMainUi):
        super().__init__(parent)
        self.user = parent.user
        self.profileBox = ProfileBox(self, self.user)
        self.editProfileButton = QPushButton("编辑资料", self)

        generalLayout = QVBoxLayout()
        generalLayout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        generalLayout.addWidget(self.profileBox)
        generalLayout.addWidget(self.editProfileButton)
        self.setLayout(generalLayout)

class GoodsList(QWidget):
    def __init__(self, parent, row=4):
        super().__init__(parent)
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setWidget(QWidget())
        self.scrollAreaLayout = QGridLayout(self.scrollArea.widget())
        self.scrollArea.widget().setLayout(self.scrollAreaLayout)
        self.row = row
        self.units = []

        generalLayout = QHBoxLayout()
        generalLayout.setContentsMargins(0, 0, 0, 0)
        generalLayout.setSpacing(0)
        generalLayout.addWidget(self.scrollArea)
        self.setLayout(generalLayout)

    def setRow(self, row):
        self.row = row
        self.updateLayout()

    def addWidgetToLayout(self, widget):
        """将部件添加到布局中"""
        index = len(self.units) - 1
        row = index // self.row
        col = index % self.row
        self.scrollAreaLayout.addWidget(widget, row, col)

    def addUnit(self, widget):
        """添加部件并存储"""
        self.units.append(widget)
        self.addWidgetToLayout(widget)

    def updateLayout(self):
        """根据rowNum重新生成布局"""
        for i in reversed(range(self.scrollAreaLayout.count())):
            item = self.scrollAreaLayout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        for index, widget in enumerate(self.units):
            row = index // self.row
            col = index % self.row
            self.scrollAreaLayout.addWidget(widget, row, col)

class ContactList(QListWidget):
    def __init__(self, parent: MessagePage):
        super().__init__(parent)
        self.user = parent.user
        self.refresh()

    def refresh(self):
        self.clear()
        Chat.refreshChats()
        chats = Chat.getChats(self.user.id)
        for row in chats:
            self.addContactListEntry(row)


    def addContactListEntry(self, uid) -> QListWidgetItem:
        _user = User(uid)
        _user.read()
        icon = MyImage(_user.hid).read().getQIcon()
        item = QListWidgetItem(_user.nickname)
        item.setIcon(icon)
        item.setSizeHint(QSize(self.width(), 60))
        item.setData(Qt.ItemDataRole.UserRole, _user.id)
        self.addItem(item)
        return item

class ChatMessageList(QWidget):
    def __init__(self, parent: MessagePage):
        super().__init__(parent)
        self.user = parent.user
        self.messages = []

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea.setWidget(QWidget(self))
        self.scrollAreaLayout = QVBoxLayout()
        self.scrollAreaLayout.addStretch()
        self.scrollArea.widget().setLayout(self.scrollAreaLayout)

        generalLayout = QVBoxLayout()
        generalLayout.addWidget(self.scrollArea)
        self.setLayout(generalLayout)

    def clear(self):
        layout = self.scrollArea.widget().layout()
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)  # 移除部件
            # 如果布局项是布局，则递归清除
            if item.layout():
                self._clear_layout(item.layout())
        self.messages.clear()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            # if isinstance(item, QSpacerItem):
            #     continue  # 跳过伸展项
            widget = item.widget()
            if widget:
                widget.setParent(None)  # 移除部件
            if item.layout():
                self._clear_layout(item.layout())

    def addMessage(self, message):
        sender_id, content, _type, time = message
        self.messages.append(message)

        is_sender = sender_id == self.user.id
        is_text = _type == "text"

        sender = User(sender_id)
        sender.read()

        widget = QWidget(self)
        messageBubble = MessageBubble(widget, (is_sender, is_text, content))
        avatar = ImageWidget(sender.hid, 40, 40, 20, widget)

        widgetLayout = QHBoxLayout()

        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Ignored)

        if is_sender:
            widgetLayout.addItem(spacer)
            widgetLayout.addWidget(messageBubble)
            widgetLayout.addWidget(avatar)
        else:
            widgetLayout.addWidget(avatar)
            widgetLayout.addWidget(messageBubble)
            widgetLayout.addItem(spacer)
        widget.setLayout(widgetLayout)

        self.scrollArea.widget().layout().addWidget(widget)
        QTimer.singleShot(100, lambda: self.scrollArea.verticalScrollBar().setValue(
            self.scrollArea.verticalScrollBar().maximum()))

    def refresh(self, uid):
        print(uid)
        self.clear()
        chat = Chat(self.user.id, uid)
        chat.readMessages()
        for message in chat.messages:
            print(message)
            self.messages.append(message)
            self.addMessage(message)

class MessageBubble(QLabel):
    def __init__(self, parent, config):
        super().__init__(parent)
        is_sender, is_text, content = config
        self.setWordWrap(True)
        self.setStyleSheet(f'''
            background-color: {'#b2e281' if is_sender else '#eeeeee'};
            border-radius: 10px;
            padding: 10px;
        ''')
        if is_text:
            self.setMaximumHeight(60)
            self.setText(content)
        else:
            pixmap = MyImage(int(content)).read().getQPixmap()
            if pixmap.width() > 900:
                pixmap = pixmap.scaledToWidth(900, Qt.TransformationMode.SmoothTransformation)
            self.setPixmap(pixmap)

class MessageEditor(QWidget):
    def __init__(self, parent: MessagePage):
        super().__init__(parent)

        self.picButton = QPushButton("发送图片", self)
        self.textEdit = QLineEdit(self)
        self.textEdit.setPlaceholderText("输入消息")
        self.sendButton = QPushButton("发送", self)

        generalLayout = QHBoxLayout()
        generalLayout.addWidget(self.picButton)
        generalLayout.addWidget(self.textEdit)
        generalLayout.addWidget(self.sendButton)
        self.setLayout(generalLayout)

class ProfileBox(QWidget):
    def __init__(self, parent, _user):
        super().__init__(parent)
        self.user = _user

        self.photo = ImageWidget(self.user.hid, 200, 200, 100, self)
        self.nameLabel = QLabel(self.user.nickname, self)
        self.idLabel = QLabel(f"ID:{self.user.id}", self)
        self.statisticsTable = QTableView(self)

        self.statisticsModel = QStandardItemModel(1, 3)
        self.statisticsModel.setHorizontalHeaderLabels(["在售", "售出", "购入"])
        self.statisticsTable.setModel(self.statisticsModel)

    def refreshStatisticsData(self):
        self.

if __name__ == '__main__':
    app = QApplication([])
    MyImage.init()
    User.init()
    Goods.init()
    user = User(10000)
    user.read()
    window = NewMainUi(user=user)
    window.show()
    app.exec()
