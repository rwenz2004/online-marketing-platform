import random
from collections.abc import Iterator

from PyQt6.QtCore import Qt, QSize, pyqtSlot, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QPalette, QStandardItemModel, QStandardItem, QFont, QDoubleValidator
from PyQt6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QApplication, QHBoxLayout, QGridLayout, QLineEdit, \
    QPushButton, QGroupBox, QVBoxLayout, QScrollArea, QLabel, QAbstractItemView, QSpacerItem, QSizePolicy, QFileDialog, \
    QTableWidget, QTableView, QHeaderView, QDial, QDialog, QPlainTextEdit, QFormLayout, QMessageBox

from chat import Chat
from goods import Goods
from image_widget import ImageWidget
from myimage import MyImage, addGoodsIconId, defaultCoverId
from user import User

class NewMainUi(QWidget):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("线上交易平台")
        self.setFixedSize(1366, 768)
        self.user = user
        self.pageSideBar = QListWidget(self)
        self.pageSideBar.setFixedWidth(80)
        self.pages = {
            "首页": HomePage(self),
            "消息": MessagePage(self),
            "我的": MyProfilePage(self),
        }

        for name in self.pages.keys():
            item = QListWidgetItem(name)
            item.setFont(QFont('微软雅黑', 20))
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

        self.pages["首页"].tryChat.connect(self.chatWith)

    def changePage(self, currentPage:QListWidgetItem, previousPage:QListWidgetItem):
        if previousPage is not None:
            self.pages[previousPage.text()].hide()
        self.pages[currentPage.text()].show()

    def chatWith(self, uid):
        # print("tryChatWith", uid)
        self.pageSideBar.setCurrentIndex(2)

        # existed = False
        # for i in range(self.messageListArea.count()):
        #     item = self.messageListArea.item(i)
        #     data = User(item.data(Qt.ItemDataRole.UserRole))
        #     if data.id == uid:
        #         existed = True
        #         self.messageListArea.setCurrentRow(i)
        #         break
        # if not existed:
        #     item = self.addMessageListEntry(uid)
        #     self.messageListArea.setCurrentItem(item)
        # parent.close()

class HomePage(QWidget):
    tryChat = pyqtSignal(int)
    def __init__(self, parent: NewMainUi):
        super().__init__(parent)
        self.user = parent.user
        #顶部搜索框
        self.searchBox = QLineEdit(self)
        self.searchBox.setPlaceholderText("输入商品名或用户名搜索")
        searchButton = QPushButton("搜索")
        searchButton.clicked.connect(lambda: self.searchFor())

        searchLayout = QHBoxLayout()
        searchLayout.addWidget(self.searchBox)
        searchLayout.addWidget(searchButton)

        #商品展示区
        self.goodsList = GoodsList(self)
        goodsIdList = Goods.getOnSaleIdList(self.user.id)
        onSaleGoodsNum = len(goodsIdList)

        for i in range(onSaleGoodsNum):
            goodsWidget = self.createGoodsWidget(self.goodsList, goodsIdList[i][0], goodsIdList[i][1])
            self.goodsList.addUnit(goodsWidget)
        self.goodsList.setRow(4)

        generalLayout = QVBoxLayout()
        generalLayout.addLayout(searchLayout)
        generalLayout.setContentsMargins(0, 0, 0, 0)
        generalLayout.setSpacing(0)
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
        detailsUi = GoodsDetailsUi(self, gid, self.user, True)
        detailsUi.messageBtn.clicked.connect(lambda: self.chatWith(gid, detailsUi))
        detailsUi.setModal(True)
        detailsUi.show()

    def showUserDetail(self, uid):
        detailsUi = UserDetailsUi(uid, self)
        detailsUi.chatBtn.clicked.connect(lambda: self.chatWith(uid, detailsUi))
        detailsUi.setModal(True)
        detailsUi.show()

    def searchFor(self):
        print(Goods.blurSearch(self.user.id, self.searchBox.text()))

    def chatWith(self, gid, parent):
        self.tryChat.emit(gid)
        parent.deleteLater()

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

    def clear(self):
        """清空units列表并从布局中移除所有部件"""
        for widget in self.units:
            widget.setParent(None)  # 从父窗口中移除部件
        self.units.clear()  # 清空units列表
        self.updateLayout()  # 更新布局以反映变化

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
        generalLayout.setContentsMargins(0, 0, 0, 0)
        generalLayout.setSpacing(0)
        generalLayout.addWidget(self.contactsList)
        generalLayout.addWidget(self.chatWidget)
        self.setLayout(generalLayout)

        self.contactsList.currentItemChanged.connect(self.openChat)
        self.messageEditor.sendButton.clicked.connect(lambda: self.sendMessage("text"))
        self.messageEditor.picButton.clicked.connect(lambda: self.sendMessage("image"))

    def openChat(self, currentChat:QListWidgetItem, _):
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

class MyProfilePage(QWidget):
    def __init__(self, parent: NewMainUi):
        super().__init__(parent)
        self.user = parent.user
        self.profileBox = ProfileBox(self, self.user)

        profileLayout = QGridLayout()
        editProfileButton = QPushButton("编辑资料", self)
        logoutButton = QPushButton("退出登录", self)
        profileLayout.addWidget(self.profileBox, 0, 1, 2, 1)
        profileLayout.addWidget(editProfileButton, 0, 3, 1, 1)
        profileLayout.addWidget(logoutButton, 1, 3, 1, 1)
        profileLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding), 0, 2, 2, 1)
        profileLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding), 0, 0, 2, 1)

        self.goodsListFilter = QListWidget(self)
        self.goodsListFilter.setFixedWidth(60)
        self.filters = {
            "全部": "%",
            "在售": "OnSale",
            "售出": "SoldOut",
            "下架": "Removed",
            "购入": "Bought"
        }
        for i in self.filters.keys():
            item = QListWidgetItem(i)
            item.setFont(QFont('微软雅黑', 14))
            self.goodsListFilter.addItem(item)

        self.goodsList = GoodsList(self)

        goodsListLayout = QHBoxLayout()
        goodsListLayout.addWidget(self.goodsListFilter)
        goodsListLayout.addWidget(self.goodsList)

        generalLayout = QVBoxLayout()
        generalLayout.setContentsMargins(0, 0, 0, 0)
        generalLayout.setSpacing(0)
        generalLayout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        generalLayout.addLayout(profileLayout)
        generalLayout.addLayout(goodsListLayout)
        self.setLayout(generalLayout)

        self.profileBox.photo.clicked.connect(lambda: self.changeProfilePhoto())
        self.goodsListFilter.currentItemChanged.connect(self.refreshGoodsList)

    def changeProfilePhoto(self):
        fileName, _ = QFileDialog.getOpenFileName(None, "选择图片", "", "Images (*.png *.xpm *.jpg)")
        if fileName:
            img = MyImage()
            img.openAt(fileName)
            img.allocId()
            img.insert()
            self.user.hid = img.id
            self.user.write()
            self.profileBox.photo.changeImageFromId(img.id)

    def refreshGoodsList(self, currentFilter: QListWidgetItem, _):
        self.goodsList.clear()
        filterStr = self.filters[currentFilter.text()]
        if filterStr == "OnSale":
            addGoodsButton = ImageWidget(addGoodsIconId, 160, 160, 5, self.goodsList)
            addGoodsButton.clicked.connect(lambda: self.addOnSaleGoods())
            self.goodsList.addUnit(addGoodsButton)
        goods = Goods.getGoodsListSatisfy(self.user.id, filterStr)
        for gid in goods:
            self.goodsList.addUnit(self.createGoodsWidget(gid))
        self.goodsList.updateLayout()

    def createGoodsWidget(self, gid):
        goodsWidget = QWidget(self.goodsList)
        goodsWidget.setFixedSize(290, 160)
        colorRange = range(5, 250)
        backgroundColor = (random.choice(colorRange), random.choice(colorRange), random.choice(colorRange))
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
        priceLabel = QLabel("¥%0.2f" % goods.price, goodsWidget)
        priceLabel.setStyleSheet("background-color: rgb(255,255,255);")
        pricePalette = QPalette()
        pricePalette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.red)
        priceLabel.setPalette(pricePalette)
        timeLabel = QLabel(f"{goods.getCreateTime()}", goodsWidget)
        timeLabel.setStyleSheet("background-color: rgb(255,255,255);")

        layout = QGridLayout()
        layout.addWidget(goodsCover, 0, 0, 3, 1)
        layout.addWidget(goodsTitle, 0, 1)
        layout.addWidget(priceLabel, 1, 1)
        layout.addWidget(timeLabel, 2, 1)
        goodsWidget.setLayout(layout)

        return goodsWidget

    def showGoodsDetail(self, gid):
        detailsUi = GoodsDetailsUi(self, gid, self.user, False)
        detailsUi.setModal(True)
        detailsUi.show()

    def addOnSaleGoods(self):
        goodsInfoEditor = GoodsInfoEditor(self, self.user.id)
        goodsInfoEditor.setModal(True)
        goodsInfoEditor.show()

class ProfileBox(QWidget):
    def __init__(self, parent, _user):
        super().__init__(parent)
        self.user = _user

        self.setFixedSize(550, 240)
        self.photo = ImageWidget(self.user.hid, 200, 200, 100, self)
        self.nameLabel = QLabel(self.user.nickname, self)
        self.nameLabel.setFont(QFont('Arial', 30))
        self.idLabel = QLabel(f"ID:{self.user.id}", self)
        self.statisticsTable = QTableView(self)

        self.statisticsModel = QStandardItemModel(0, 3)
        self.statisticsModel.setHorizontalHeaderLabels(["在售", "售出", "购入"])
        self.statisticsTable.setModel(self.statisticsModel)
        self.statisticsTable.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.statisticsTable.verticalHeader().hide()
        self.statisticsTable.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.statisticsTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.statisticsTable.setFixedSize(300, 80)

        self.refreshStatisticsData()

        generalLayout = QGridLayout()
        generalLayout.addWidget(self.photo, 0, 0, 3, 1)
        generalLayout.addWidget(self.nameLabel, 0, 1, 1, 2)
        generalLayout.addWidget(self.idLabel, 1, 1, 1, 1)
        generalLayout.addWidget(self.statisticsTable, 2, 1, 1, 2)
        self.setLayout(generalLayout)

    def refreshStatisticsData(self):
        data = self.user.getStatistics()
        items = []
        for i in data:
            print(i)
            item = QStandardItem(str(i))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            items.append(item)
        self.statisticsModel.removeRow(0)
        self.statisticsModel.insertRow(0, items)

class GoodsInfoEditor(QDialog):
    def __init__(self, parent, uid):
        super().__init__(parent)
        self.setWindowTitle("上架商品")
        self.uid = uid
        self.coverPath = ""
        self.setFixedSize(600, 400)

        self.titleEditor = QLineEdit(self)
        self.titleEditor.setFixedWidth(240)
        self.priceEditor = QLineEdit(self)
        validator = QDoubleValidator(0.00, 999999.99, 2, self.priceEditor)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.priceEditor.setValidator(validator)
        self.priceEditor.setFixedWidth(60)
        self.coverEditor = ImageWidget(defaultCoverId, 140, 140, 15, self)
        self.descriptionEditor = QPlainTextEdit(self)

        editAreaLayout = QFormLayout()
        editAreaLayout.addRow("添加名称", self.titleEditor)
        editAreaLayout.addRow("价格(¥)", self.priceEditor)
        editAreaLayout.addRow("添加封面", self.coverEditor)
        editAreaLayout.addRow("添加描述", self.descriptionEditor)

        uploadButton = QPushButton("上架")
        uploadButton.setFixedWidth(50)

        generalLayout = QGridLayout()
        generalLayout.addLayout(editAreaLayout, 0, 0, 1, 2)
        generalLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred), 1, 0, 1, 1)
        generalLayout.addWidget(uploadButton, 1, 1, 1, 1)
        self.setLayout(generalLayout)

        self.coverEditor.clicked.connect(lambda: self.chooseCover())
        uploadButton.clicked.connect(lambda: self.validateInput())

    def chooseCover(self):
        fileName, _ = QFileDialog.getOpenFileName(None, "选择图片", "", "Images (*.png *.xpm *.jpg)")
        if fileName:
            self.coverPath = fileName
            self.coverEditor.changeImageFromPath(fileName)

    def validateInput(self):
        if self.titleEditor.text() == "":
            QMessageBox(QMessageBox.Icon.Warning, "检查输入", "名称不能为空", QMessageBox.StandardButton.Ok).exec()
        if self.priceEditor.text() == "":
            QMessageBox(QMessageBox.Icon.Warning, "检查输入", "价格不能为空", QMessageBox.StandardButton.Ok).exec()
        if self.descriptionEditor.toPlainText() == "":
            QMessageBox(QMessageBox.Icon.Warning, "检查输入", "描述不能为空", QMessageBox.StandardButton.Ok).exec()

        cid = defaultCoverId
        if len(self.coverPath) > 0:
            image = MyImage()
            image.allocId()
            image.openAt(self.coverPath)
            image.insert()
            cid = image.id

        _goods = Goods()
        _goods.allocId()
        _goods.status = "OnSale"
        (_goods.name, _goods.price, _goods.description, _goods.uid, _goods.cid) \
            = (self.titleEditor.text(), float(self.priceEditor.text()), self.descriptionEditor.toPlainText(), self.uid, cid)
        _goods.insert()
        QMessageBox(QMessageBox.Icon.Information, "添加成功", "成功上架！", QMessageBox.StandardButton.Ok).exec()
        self.deleteLater()

class GoodsDetailsUi(QDialog):
    exited = pyqtSignal()
    def __init__(self, parent, gid, _user, is_on_sale):
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

        generalLayout = QVBoxLayout()
        generalLayout.addWidget(self.textArea)
        generalLayout.addSpacerItem(QSpacerItem(self.width(), 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        if is_on_sale:
            self.bottomArea = QWidget(self)
            self.commentBtn = QPushButton("评论", self)
            self.collectBtn = QPushButton("收藏", self)
            self.messageBtn = QPushButton("联系卖家", self)
            self.purchaseBtn = QPushButton("购买", self)
            self.purchaseBtn.clicked.connect(lambda: self.purchase())

            bottomArea = QHBoxLayout()
            bottomArea.addWidget(self.commentBtn)
            bottomArea.addWidget(self.collectBtn)
            bottomArea.addSpacing(600)
            bottomArea.addWidget(self.messageBtn)
            bottomArea.addWidget(self.purchaseBtn)
            self.bottomArea.setLayout(bottomArea)
            generalLayout.addWidget(self.bottomArea)

        self.setLayout(generalLayout)

    def purchase(self):
        if self.user.purchase(self.goods.id):
            QMessageBox.information(self, "购买成功", "下单成功, 等待卖家发货.")
            self.close()
        else:
            QMessageBox.warning(self, "购买失败", "下单失败.")

    def closeEvent(self, event):
        self.exited.emit()
        QDialog.closeEvent(self, event)

class UserDetailsUi(QDialog):
    def __init__(self, uid, parent):
        super().__init__(parent)
        self.user = User(uid)
        self.user.read()
        self.setWindowTitle(f"{self.user.nickname}的主页")
        self.setFixedSize(600, 240)

        self.profileBox = ProfileBox(self, self.user)
        self.chatBtn = QPushButton("聊天", self)

        generalLayout = QHBoxLayout()
        generalLayout.addWidget(self.profileBox)
        generalLayout.addWidget(self.chatBtn)
        self.setLayout(generalLayout)

if __name__ == '__main__':
    app = QApplication([])
    MyImage.init()
    User.init()
    Goods.init()
    user = User(10001)
    user.read()
    window = NewMainUi(user=user)
    window.show()
    app.exec()
