import sys

from PyQt6.QtWidgets import QApplication

from goods import Goods
from login_ui import LoginUi
from myimage import MyImage
from user import User

def main():
    app = QApplication(sys.argv)

    # MyImage.init()
    # User.init()
    Goods.init()

    login = LoginUi()
    login.exec()

    #测试用
    # user = User(10000)
    # user.read()
    # mainUi = MainUi(user)
    # mainUi.show()
    # user.allocId()
    # user.nickname = f"用户{user.id}"
    # user.telephone = str(150_0000_0000 + user.id)
    # user.password = f"pwd{user.id}"
    # user.insert()
    #
    # for i in range(3):
    #     goods = Goods()
    #     goods.allocId()
    #     goods.uid = user.id
    #     goods.name = f"商品{goods.id}"
    #     goods.status = 'OnSale'
    #     goods.insert()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()



