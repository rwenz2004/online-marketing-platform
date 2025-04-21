from PyQt6.QtCore import Qt, QRegularExpression, pyqtSlot, pyqtSignal, QEventLoop
from PyQt6.QtGui import QIntValidator, QRegularExpressionValidator, QFont, QPalette
from PyQt6.QtWidgets import QWidget, QDialog, QPushButton, QRadioButton, QLineEdit, QLabel, QFormLayout, QGridLayout, \
    QHBoxLayout, QVBoxLayout, QButtonGroup, QFileDialog, QSpacerItem, QSizePolicy, QMenu, QMessageBox

from image_widget import ImageWidget
from myimage import defaultPhotoId, MyImage
from new_main_ui import NewMainUi
from user import User
import re

class LoginUi(QDialog):

    def __init__(self):
        super().__init__()
        self.user = User()
        self.mainWindow = None
        self.setWindowTitle("线上交易平台")
        self.setFixedSize(270, 300)
        self.setWindowFlags(Qt.WindowType.Tool)

        #选择框
        chooseWidget = QWidget(self)
        chooseWidget.setMaximumHeight(40)
        self.loginRdbtn = QRadioButton("登录", self)
        self.loginRdbtn.clicked.connect(lambda: self.switchPage())
        self.registerRdbtn = QRadioButton("注册", self)
        self.registerRdbtn.clicked.connect(lambda: self.switchPage())

        chooseGroup = QButtonGroup(self)
        chooseGroup.addButton(self.loginRdbtn)
        chooseGroup.addButton(self.registerRdbtn)
        self.loginRdbtn.setChecked(True)
        chooseWidgetLayout = QHBoxLayout()
        chooseWidgetLayout.addWidget(self.loginRdbtn)
        chooseWidgetLayout.addWidget(self.registerRdbtn)
        chooseWidgetLayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Ignored))
        chooseWidget.setLayout(chooseWidgetLayout)


        #登录页面
        self.loginWidget = QWidget(self)

        self.accountEdit = QLineEdit(self.loginWidget)
        self.accountEdit.setPlaceholderText("在此输入账号")
        self.accountEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]+")))
        self.accountEdit.textChanged.connect(lambda: self.onAccountEditChanged())

        self.passwordEdit = QLineEdit(self.loginWidget)
        self.passwordEdit.setPlaceholderText("在此输入密码")
        self.passwordEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.passwordEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[a-zA-Z0-9]+")))

        self.loginBtn = QPushButton("登录", self.loginWidget)
        self.loginBtn.clicked.connect(self.checkLoginInput)

        self.loginInfo = QLabel(self.loginWidget)
        self.loginInfo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.red)
        self.loginInfo.setPalette(palette)

        self.photoFrame = QWidget(self.loginWidget)
        self.photo = ImageWidget(defaultPhotoId, 60, 60, 30, self.photoFrame)
        photoLayout = QHBoxLayout()
        photoLayout.addWidget(self.photo)
        self.photoFrame.setLayout(photoLayout)

        inputLayout = QFormLayout()
        inputLayout.addRow("账号", self.accountEdit)
        inputLayout.addRow("密码", self.passwordEdit)

        loginLayout = QGridLayout()
        loginLayout.addWidget(self.photoFrame, 1, 0, 1, 3)
        loginLayout.addLayout(inputLayout, 2, 0, 1, 3)
        loginLayout.addWidget(self.loginInfo, 3, 0, 1, 3)
        loginLayout.addWidget(self.loginBtn, 4, 1, 1, 1)

        self.loginWidget.setLayout(loginLayout)

        self.registerWidget = QWidget(self)

        self.registerImg = MyImage(defaultPhotoId)
        self.registerPhoto = ImageWidget(defaultPhotoId, 60, 60, 30, self.registerWidget)
        self.registerChangePhoto = QPushButton("更换头像", self.registerWidget)
        self.registerChangePhoto.clicked.connect(lambda: self.changeRegisterPhoto())
        registerPhotoWidget = QWidget(self.registerWidget)
        registerPhotoWidgetLayout = QHBoxLayout()
        registerPhotoWidgetLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        registerPhotoWidgetLayout.addWidget(self.registerPhoto)
        registerPhotoWidgetLayout.addWidget(self.registerChangePhoto)
        registerPhotoWidget.setLayout(registerPhotoWidgetLayout)

        self.registerTeleEdit = QLineEdit(self.registerWidget)
        self.registerTeleEdit.setPlaceholderText("输入手机号")
        self.registerNameEdit = QLineEdit(self.registerWidget)
        self.registerNameEdit.setPlaceholderText("输入昵称(2~8个中英文或数字字符)")
        self.registerPasswordEdit = QLineEdit(self.registerWidget)
        self.registerPasswordEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.registerPasswordEdit.setPlaceholderText("输入密码(6~20字符)")
        self.registerRepeatEdit = QLineEdit(self.registerWidget)
        self.registerRepeatEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.registerRepeatEdit.setPlaceholderText("重复密码")
        self.registerBtn = QPushButton("注册", self.registerWidget)
        self.registerBtn.clicked.connect(lambda: self.tryRegister())
        self.registerBtn.setMaximumWidth(self.width() // 3)

        registerInputWidget = QWidget(self.registerWidget)
        self.registerInfo = QLabel(self.registerWidget)
        self.registerInfo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        registerInputLayout = QFormLayout()
        registerInputLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        registerInputLayout.addRow("手机", self.registerTeleEdit)
        registerInputLayout.addRow("昵称", self.registerNameEdit)
        registerInputLayout.addRow("密码", self.registerPasswordEdit)
        registerInputLayout.addRow("确认密码", self.registerRepeatEdit)
        registerInputWidget.setLayout(registerInputLayout)

        registerLayout = QVBoxLayout()
        registerLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        registerLayout.addWidget(registerPhotoWidget)
        registerLayout.addWidget(registerInputWidget)
        registerLayout.addWidget(self.registerInfo)
        registerLayout.addWidget(self.registerBtn)
        self.registerWidget.setLayout(registerLayout)

        generalLayout = QVBoxLayout()
        generalLayout.setSpacing(0)
        generalLayout.setContentsMargins(0, 0, 0, 0)
        generalLayout.addWidget(chooseWidget)
        generalLayout.addWidget(self.loginWidget)
        generalLayout.addWidget(self.registerWidget)
        self.setLayout(generalLayout)
        self.switchPage()

    def closeEvent(self, event):
        QDialog.closeEvent(self, event)
        exit(0)

    def checkLoginInput(self):
        self.loginInfo.clear()
        account = self.accountEdit.text()
        password = self.passwordEdit.text()
        if len(account) == 0 or len(password) == 0:
            self.loginInfo.setText("账号和密码不能为空")
            return
        self.user.id = int(account)

        if not self.user.read():
            self.loginInfo.setText("账号不存在")
            return
        if not self.user.password == password:
            self.loginInfo.setText("密码错误")
            self.passwordEdit.clear()
            return

        self.login()

    def onAccountEditChanged(self):
        # print("account:", self.accountEdit.text())
        if len(self.accountEdit.text()) > 0:
            # print("searching:", self.accountEdit.text())
            uid = int(self.accountEdit.text())
            if User.existedId(uid):
                user = User(uid)
                user.read()
                self.photo.changeImageFromId(user.hid)
                return
        self.photo.changeImageFromId(defaultPhotoId)

    def switchPage(self):
        if self.loginRdbtn.isChecked():
            self.loginWidget.show()
            self.registerWidget.hide()
        elif self.registerRdbtn.isChecked():
            self.loginWidget.hide()
            self.registerWidget.show()

    def login(self):
        self.mainWindow = NewMainUi(self.user)
        self.mainWindow.show()
        self.deleteLater()

    def changeRegisterPhoto(self):
        imgPath, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.xpm *.jpg)")
        if imgPath:
            self.registerImg.id = None
            self.registerImg.openAt(imgPath)
            self.registerPhoto.changeImageFromQPixmap(self.registerImg.getQPixmap())

    def tryRegister(self):
        self.registerInfo.clear()
        telePattern = r'^1[3-9]\d{9}$'
        namePattern = r'^[\u4e00-\u9fa5a-zA-Z0-9]{2,8}$'
        passwordPattern =  r'^[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\'\\:"|,.<>\/?]{6,20}$'
        if not re.match(telePattern, self.registerTeleEdit.text()):
            self.registerTeleEdit.clear()
            self.registerInfo.setText("手机号不合法, 请输入中国大陆手机号")
            return
        if User.existedTelephone(self.registerTeleEdit.text()):
            self.registerTeleEdit.clear()
            self.registerInfo.setText("手机号已注册")
            return
        if not re.match(namePattern, self.registerNameEdit.text()):
            self.registerNameEdit.clear()
            self.registerInfo.setText("昵称不合法, 必须为2~8字符的中英文及数字组合")
            return
        if not re.match(passwordPattern, self.registerPasswordEdit.text()):
            self.registerPasswordEdit.clear()
            self.registerRepeatEdit.clear()
            self.registerInfo.setText("密码不合法, 请检查输入")
            return
        if not (self.registerPasswordEdit.text() == self.registerRepeatEdit.text()):
            self.registerPasswordEdit.clear()
            self.registerRepeatEdit.clear()
            self.registerInfo.setText("密码输入不一致")
            return
        self.user.allocId()
        self.user.nickname = self.registerNameEdit.text()
        self.user.telephone = self.registerTeleEdit.text()
        self.user.password = self.registerPasswordEdit.text()
        if self.registerImg.id is None:
            self.registerImg.allocId()
            self.registerImg.insert()
        self.user.hid = self.registerImg.id
        self.user.insert()
        self.accountEdit.setText(f"{self.user.id}")
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("注册成功")
        msg.setText(f"注册成功!您的账号是: {self.user.id}, 请牢记")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
        self.loginRdbtn.setChecked(True)
        self.switchPage()


