import sys

from PyQt6.QtWidgets import QApplication

from database import db
from goods import Goods
from login_ui import LoginUi
from main_ui import MainUi
from myimage import MyImage
from user import User


def createTables():
    db.exec('''
        pragma foreign_keys=ON
    ''')
    db.exec('''
        create table
        if not exists image(
            id integer primary key,
            data blob not null
        )
    ''')
    db.exec('''
        create table
        if not exists user(
            id integer primary key,
            hid integer not null,
            nickname text not null,
            password text not null,
            telephone text not null,
            foreign key (hid) references image(id) on delete cascade
        )
    ''')
    db.exec('''
        create table 
        if not exists goods(
            id integer primary key,
            uid integer not null,
            cid integer not null,
            name text not null,
            price real not null,
            time datetime default CURRENT_TIMESTAMP,
            status text check(status in ('OnSale','SoldOut', 'Removed', 'Unknown')),
            description text not null,
            foreign key (uid) references user(id) on delete cascade
            foreign key (cid) references image(id) on delete cascade
        )
    ''')
    db.exec('''
        create table
        if not exists purchase(
            uid integer not null,
            gid integer not null,
            price real not null,
            time datetime default CURRENT_TIMESTAMP,
            primary key (uid, gid),
            foreign key (uid) references user(id) on delete cascade
            foreign key (gid) references goods(id) on delete cascade
        )
    ''')
    db.exec('''
        create table
        if not exists message(
            id integer primary key autoincrement,
            sender integer not null,
            receiver integer not null,
            type text check(type in ('text', 'image')),
            content text not null,
            time datetime default CURRENT_TIMESTAMP,
            foreign key (sender) references user(id) on delete cascade,
            foreign key (receiver) references user(id) on delete cascade,
            check(sender <> receiver)
        )
    ''')

    db.exec('''
        create view
        if not exists
        onsale_goods as
        select
            goods.uid,
            goods.id as gid
        from
            goods
        where
            goods.status = 'OnSale'
    ''')

    db.exec('''
        create view
        if not exists
        chat as
        select distinct
            case
                when sender < receiver then sender || '-' || receiver 
                else receiver || '-' || sender 
            end as id
        from message;
    ''')

    db.exec('''
        create view
        if not exists
        statistics as
        SELECT 
            u.id AS uid,
            COALESCE(SUM(CASE WHEN g.status = 'OnSale' THEN 1 ELSE 0 END), 0) AS on_sale_count,
            COALESCE(COUNT(DISTINCT p.gid), 0) AS purchased_count,
            COALESCE(COUNT(DISTINCT s.gid), 0) AS sold_count
        FROM 
            user u
        LEFT JOIN 
            goods g ON u.id = g.uid AND g.status = 'OnSale'
        LEFT JOIN 
            purchase p ON u.id = p.uid
        LEFT JOIN 
            purchase s ON u.id = (SELECT g.uid FROM goods g WHERE g.id = s.gid)
        GROUP BY 
            u.id;
    ''')

def main():
    app = QApplication(sys.argv)

    createTables()
    MyImage.init()
    User.init()
    Goods.init()

    # login = LoginUi()
    # login.exec()

    #测试用
    user = User(10000)
    user.read()
    mainUi = MainUi(user)
    mainUi.show()
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



