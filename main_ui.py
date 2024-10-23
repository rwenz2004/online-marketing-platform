import random

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPainter, QPalette
from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QRadioButton, QButtonGroup, \
    QGridLayout, QStyleOption, QStyle, QLineEdit, QSpacerItem, QScrollArea, QLabel, \
    QFileDialog, QSizePolicy, QListWidget, QListWidgetItem, QAbstractItemView

from chat import Chat
from details_ui import GoodsDetailsUi, UserDetailsUi
from goods import Goods
from image_widget import ImageWidget
from myimage import MyImage
from user import User


class MainUi(QWidget):
    def __init__(self, _user):
        super().__init__()

        self.homeGoodsRowNum = 5
        self.homeGoodsColNum = 4

        self.user = _user
        self.setWindowTitle('Online Marketing Platform')
        self.setFixedSize(1366, 768)
        # self.setStyleSheet('padding: 0px')

        #侧边栏初始化
        self.sideBar = QWidget(self)
        self.sideBar.setObjectName("sideBar")
        self.sideBar.setFixedSize(120, self.height())

        sideBarLayout = QVBoxLayout()
        sideBarLayout.setContentsMargins(0, 0, 0, 0)
        sideBarLayout.setSpacing(0)

        self.homeBtn = QRadioButton('首页', self.sideBar)
        self.messageBtn = QRadioButton('消息', self.sideBar)
        self.profileBtn = QRadioButton('我的', self.sideBar)
        self.settingsBtn = QRadioButton('设置', self.sideBar)

        sideBarButtonGroup = QButtonGroup(self.sideBar)
        sideBarButtonGroup.addButton(self.homeBtn)
        sideBarButtonGroup.addButton(self.messageBtn)
        sideBarButtonGroup.addButton(self.profileBtn)
        sideBarButtonGroup.addButton(self.settingsBtn)

        sideBarButtons = [self.homeBtn, self.messageBtn, self.profileBtn, self.settingsBtn]

        for i in range(len(sideBarButtons)):
            # print(sideBarButtons[i], i)
            sideBarButtons[i].setFont(QFont('微软雅黑', 14))
            sideBarButtons[i].setFixedSize(self.sideBar.width(), 50)
            sideBarLayout.addWidget(sideBarButtons[i])
            sideBarButtons[i].clicked.connect(lambda: self.changePage())

        sideBarLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.sideBar.setLayout(sideBarLayout)
        # self.sideBar.setStyleSheet('''
        #     QWidget#sideBar {
        #         background-color: #1976D2;
        #     }
        #     QWidget#sideBar > QRadioButton {
        #         background-color: #2196F3;
        #         color: white;
        #         border: none;
        #         padding: 0px;
        #         text-align: center;
        #         text-decoration: none;
        #         display: inline-block;
        #         font-size: 16px;
        #         margin: 0px;
        #         cursor: pointer;
        #         border-radius: 0px;
        #     }
        #     QWidget#sideBar > QRadioButton::indicator {
        #         width: 0px;
        #         height: 0px;
        #     }
        #     QWidget#sideBar > QRadioButton::checked {
        #         background-color: #1976D2;
        #     }
        # ''')

        #首页初始化
        self.homeWidget = QWidget(self)
        self.homeWidget.setObjectName("homeWidget")
        self.homeWidget.setFixedSize(self.width() - self.sideBar.width(), self.height())
        # self.homeWidget.setStyleSheet("background-color: #1976D2;")

        self.homeSearchEdit = QLineEdit(self.homeWidget)
        self.homeSearchEdit.setFixedSize(int(self.homeWidget.width() * 0.4), 30)
        self.homeSearchBtn = QPushButton(self.homeWidget)
        self.homeSearchBtn.setFixedSize(40, self.homeSearchBtn.height())

        self.homeGoodsArea = QScrollArea(self.homeWidget)
        self.homeGoodsArea.setWidgetResizable(True)

        self.refreshGoodsArea()

        homeWidgetLayout = QGridLayout()
        homeWidgetLayout.setContentsMargins(0, 0, 0, 0)
        homeWidgetLayout.setSpacing(0)
        homeWidgetLayout.addItem(
            QSpacerItem( 0, 0, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Ignored),
            0, 0, 1, 1
        )
        homeWidgetLayout.addWidget(self.homeSearchEdit, 0, 1, 1, 2)
        homeWidgetLayout.addWidget(self.homeSearchBtn, 0, 3, 1, 1)
        homeWidgetLayout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Ignored),
            0, 4, 1, 1
        )
        homeWidgetLayout.addWidget(self.homeGoodsArea, 1, 0, 1, 5)

        self.homeWidget.setLayout(homeWidgetLayout)

        #消息页初始化
        self.messageWidget = QWidget(self)
        self.messageWidget.setObjectName("messageWidget")
        self.messageWidget.setFixedSize(self.width() - self.sideBar.width(), self.height())

        self.messageListArea = QListWidget(self.messageWidget)
        self.messageListArea.setMinimumWidth(200)
        self.messageListArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.messageListArea.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.messageListArea.setIconSize(QSize(50, 50))
        self.refreshMessageList()

        self.chatWidget = QWidget(self.messageWidget)
        self.chatWidget.setFixedSize(self.width() - self.sideBar.width() - self.messageListArea.width(), self.height())
        self.chatUserName = QLabel(self.chatWidget)

        self.chatArea = QScrollArea()
        self.chatArea.setWidgetResizable(True)
        self.chatArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.chatArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        choosePicBtn = QPushButton("发送图片", self.chatWidget)
        choosePicBtn.clicked.connect(lambda: self.sendMessage("image"))
        choosePicBtn.setMinimumHeight(50)
        self.chatEdit = QLineEdit(self.chatWidget)
        self.chatEdit.setPlaceholderText("输入消息")
        self.chatEdit.setMinimumHeight(50)
        self.sendBtn = QPushButton("发送", self.chatWidget)
        self.sendBtn.setMinimumHeight(50)
        self.sendBtn.setDisabled(True)
        self.sendBtn.clicked.connect(lambda: self.sendMessage("text"))

        self.chatEdit.textChanged.connect(lambda: self.chatTextChanged())

        chatWidgetLayout = QGridLayout()
        chatWidgetLayout.addWidget(self.chatUserName, 0, 0, 1, 1)
        chatWidgetLayout.addWidget(self.chatArea, 1, 0, 1, 3)
        chatWidgetLayout.addWidget(choosePicBtn, 2, 0, 1, 1)
        chatWidgetLayout.addWidget(self.chatEdit, 2, 1, 1, 1)
        chatWidgetLayout.addWidget(self.sendBtn, 2, 2, 1, 1)
        self.chatWidget.setLayout(chatWidgetLayout)
        self.refreshChatWidget()

        messageWidgetLayout = QHBoxLayout()
        messageWidgetLayout.addWidget(self.messageListArea)
        messageWidgetLayout.addWidget(self.chatWidget)

        self.messageWidget.setLayout(messageWidgetLayout)

        #个人页初始化
        self.profileWidget = QWidget(self)
        self.profileWidget.setObjectName("profileWidget")
        self.profileWidget.setFixedSize(self.width() - self.sideBar.width(), self.height())

        self.profilePhoto = ImageWidget(self.user.hid, 200, 200, 100, self.profileWidget)

        self.profileChangePhotoBtn = QPushButton("更换头像", self.profileWidget)
        self.profileChangePhotoBtn.clicked.connect(lambda: self.changeProfilePhoto())

        profileGoodsWidget = QWidget(self.profileWidget)

        self.profileList = QListWidget(profileGoodsWidget)
        self.profileList.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.profileList.setFixedWidth(150)
        self.profileList.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        listWidgetLabels = ["我的售出", "我的买入", "我的收藏"]
        for label in listWidgetLabels:
            item = QListWidgetItem(label, self.profileList)
            item.setSizeHint(QSize(self.profileList.width(), 60))
            self.profileList.addItem(item)

        self.profileSoldGoodsWidget = QWidget(profileGoodsWidget)

        profileGoodsWidgetLayout = QHBoxLayout()
        profileGoodsWidgetLayout.addWidget(self.profileList)
        profileGoodsWidgetLayout.addWidget(self.profileSoldGoodsWidget)
        profileGoodsWidget.setLayout(profileGoodsWidgetLayout)

        profileWidgetLayout = QVBoxLayout()
        profileWidgetLayout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        profileWidgetLayout.addWidget(self.profilePhoto)
        profileWidgetLayout.addWidget(self.profileChangePhotoBtn)
        profileWidgetLayout.addWidget(profileGoodsWidget)

        self.profileWidget.setLayout(profileWidgetLayout)

        #设置页初始化
        self.settingsWidget = QWidget(self)
        self.settingsWidget.setObjectName("settingsWidget")
        self.settingsWidget.setFixedSize(self.width() - self.sideBar.width(), self.height())
        self.settingsArea = QScrollArea(self.settingsWidget)
        self.settingsArea.setWidgetResizable(True)

        #布局相关设置
        generalLayout = QHBoxLayout()
        generalLayout.setContentsMargins(0,0,0,0)
        generalLayout.setSpacing(0)
        generalLayout.addWidget(self.sideBar)
        generalLayout.addWidget(self.homeWidget)
        generalLayout.addWidget(self.messageWidget)
        generalLayout.addWidget(self.profileWidget)
        generalLayout.addWidget(self.settingsWidget)

        self.setLayout(generalLayout)

        self.homeBtn.setChecked(True)
        self.changePage()

        #样式设置
        qss = open("./main_ui.qss", 'r')
        qssStr = qss.read()
        # print(qssStr)
        # self.setStyleSheet(qssStr)
        # self.setStyleSheet('''
        #     QWidget {
        #         background-color: #1976D2;
        #     }
        # ''')
        # print(self.__class__)
        # print(self.styleSheet())
 
    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)
        QWidget.paintEvent(self, event)

    def changePage(self, _id = None):
        if _id is not None:
            match _id:
                case 1:
                    self.homeBtn.setChecked(True)
                case 2:
                    self.messageBtn.setChecked(True)
                case 3:
                    self.profileBtn.setChecked(True)
                case 4:
                    self.settingsBtn.setChecked(True)
        if self.homeBtn.isChecked():
            self.refreshGoodsArea()
            self.homeWidget.show()
            self.messageWidget.hide()
            self.profileWidget.hide()
            self.settingsWidget.hide()
        if self.messageBtn.isChecked():
            self.refreshMessageList()
            self.messageWidget.show()
            self.homeWidget.hide()
            self.profileWidget.hide()
            self.settingsWidget.hide()
        if self.profileBtn.isChecked():
            self.profileWidget.show()
            self.homeWidget.hide()
            self.messageWidget.hide()
            self.settingsWidget.hide()
        if self.settingsBtn.isChecked():
            self.settingsWidget.show()
            self.homeWidget.hide()
            self.messageWidget.hide()
            self.profileWidget.hide()

    def refreshGoodsArea(self):
        if self.homeGoodsArea.widget() is not None:
            self.homeGoodsArea.widget().deleteLater()

        homeGoodsContainer = QWidget()

        goodsIdList = Goods.getOnSaleIdList(self.user.id)
        onSaleGoodsNum = len(goodsIdList)

        homeGoodsContainerLayout = QGridLayout(homeGoodsContainer)

        for i in range(onSaleGoodsNum):
            goodsWidget = self.createGoodsWidget(homeGoodsContainer, goodsIdList[i][0],goodsIdList[i][1])
            # print(i, i // self.homeGoodsColNum, i % self.homeGoodsColNum)
            homeGoodsContainerLayout.addWidget(goodsWidget, i // self.homeGoodsColNum, i % self.homeGoodsColNum )

        self.homeGoodsArea.setWidget(homeGoodsContainer)

        # print("on sale goods num:", onSaleGoodsNum)

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
        detailsUi.exited.connect(lambda: self.refreshGoodsArea())
        goods = Goods(gid)
        goods.read()
        detailsUi.messageBtn.clicked.connect(lambda: self.chatWith(goods.uid, detailsUi))
        detailsUi.setModal(True)
        detailsUi.show()

    def showUserDetail(self, uid):
        detailsUi = UserDetailsUi(uid, self)
        detailsUi.chatBtn.clicked.connect(lambda: self.chatWith(uid, detailsUi))
        detailsUi.setModal(True)
        detailsUi.show()

    def addMessageListEntry(self, uid) -> QListWidgetItem:
        user = User(uid)
        user.read()
        icon = MyImage(user.hid).read().getQIcon()
        item = QListWidgetItem(user.nickname)
        item.setIcon(icon)
        item.setSizeHint(QSize(self.messageListArea.width(), 60))
        item.setData(Qt.ItemDataRole.UserRole, user.id)
        self.messageListArea.addItem(item)
        return item

    def chatWith(self, uid, parent):
        self.changePage(2)
        existed = False
        for i in range(self.messageListArea.count()):
            item = self.messageListArea.item(i)
            data = User(item.data(Qt.ItemDataRole.UserRole))
            if data.id == uid:
                existed = True
                self.messageListArea.setCurrentRow(i)
                break
        if not existed:
            item = self.addMessageListEntry(uid)
            self.messageListArea.setCurrentItem(item)
        parent.close()

    def refreshMessageList(self):
        self.messageListArea.clear()
        Chat.refreshChats()
        chats = Chat.getChats(self.user.id)
        for row in chats:
            self.addMessageListEntry(row)
        self.messageListArea.currentItemChanged.connect(lambda: self.refreshChatWidget(
        self.messageListArea.currentItem().data(Qt.ItemDataRole.UserRole)
        if self.messageListArea.currentItem() is not None else None
        ))

    def refreshChatWidget(self, uid = None):
        if uid is None:
            self.chatWidget.hide()
        else:
            user = User(uid)
            user.read()
            self.chatUserName.setText(user.nickname)
            self.refreshChatArea(uid)
            self.chatWidget.show()

    def refreshChatArea(self, uid):
        if self.chatArea.widget() is not None:
            self.chatArea.widget().deleteLater()

        chat = Chat(self.user.id, uid)
        chat.readMessages()

        chatContent = QWidget()
        chatContentLayout = QVBoxLayout(chatContent)
        chatContentLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        for message in chat.messages:
            self.addChatMessage(message, chatContentLayout, chatContent)
        chatContentLayout.addStretch()
        self.chatArea.setWidget(chatContent)
        self.chatArea.verticalScrollBar().setValue(self.chatArea.verticalScrollBar().maximum())

    def chatTextChanged(self):
        if len(self.chatEdit.text()) < 1:
            self.sendBtn.setDisabled(True)
        else:
            self.sendBtn.setDisabled(False)

    def sendMessage(self, _type = "text"):
        if self.messageListArea.currentItem() is None:
            return
        uid = self.messageListArea.currentItem().data(Qt.ItemDataRole.UserRole)
        chat = Chat(self.user.id, uid)
        if _type == "text":
            content = self.chatEdit.text()
            self.chatEdit.setText("")
            chat.insert(content, _type)
            self.refreshChatArea(uid)
        elif _type == "image":
            fileName, _ = QFileDialog.getOpenFileName(None, "选择图片", "", "Images (*.png *.xpm *.jpg)")
            # print(fileName)
            if fileName:
                img = MyImage()
                img.openAt(fileName)
                img.allocId()
                img.insert()
                chat.insert(str(img.id), _type)
                self.refreshChatArea(uid)

    def addChatMessage(self, message, layout, parent):
        sender_id, content, _type, time = message
        is_sender = sender_id==self.user.id
        widget = QWidget(parent)

        chatBubble = QLabel(widget)
        chatBubble.setWordWrap(True)

        chatBubble.setStyleSheet(f'''
            background-color: {'#b2e281' if is_sender else '#eeeeee'};
            border-radius: 10px;
            padding: 10px;
        ''')

        if _type == 'text':
            widget.setMaximumHeight(60)
            chatBubble.setText(content)
        else:
            pixmap = MyImage(int(content)).read().getQPixmap()
            if pixmap.width() > 900:
                pixmap = pixmap.scaledToWidth(900, Qt.TransformationMode.SmoothTransformation)
            chatBubble.setPixmap(pixmap)
            # chatBubble.setScaledContents(True)
        sender = User(sender_id)
        sender.read()

        avatar = ImageWidget(sender.hid, 40, 40, 20, widget)

        widgetLayout = QHBoxLayout()
        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Ignored)
        if is_sender:
            widgetLayout.addItem(spacer)
            widgetLayout.addWidget(chatBubble)
            widgetLayout.addWidget(avatar)
        else:
            widgetLayout.addWidget(avatar)
            widgetLayout.addWidget(chatBubble)
            widgetLayout.addItem(spacer)
        widget.setLayout(widgetLayout)
        layout.addWidget(widget)

    def changeProfilePhoto(self):
        fileName, _ = QFileDialog.getOpenFileName(None, "选择图片", "", "Images (*.png *.xpm *.jpg)")
        if fileName:
            img = MyImage()
            img.openAt(fileName)
            img.allocId()
            img.insert()
            self.user.hid = img.id
            self.user.write()
            self.profilePhoto.changeImageFromId(img.id)
