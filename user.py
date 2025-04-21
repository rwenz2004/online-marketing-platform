from database import db
from goods import Goods
from myimage import defaultPhotoId


class User:
    #静态属性
    nextId = 10000

    #静态方法
    @staticmethod
    def init():

        db.exec("select MAX(id) from user")
        result = db.cursor.fetchone()
        if result[0] is not None:
            User.nextId = result[0] + 1

    @staticmethod
    def existedId(_id) -> bool:
        db.exec('''
            select id 
            from user 
            where id = ?
        ''', (_id,))
        if db.cursor.fetchone() is None:
            return False
        return True

    @staticmethod
    def existedTelephone(telephone) -> bool:
        db.exec('''
            select id 
            from user 
            where telephone like ?
        ''', (telephone,))
        if db.cursor.fetchone() is None:
            return False
        return True

    #方法
    def __init__(self, _id = 0):
        self.id = _id
        self.hid = defaultPhotoId
        self.nickname = "昵称五个字"
        self.password = "password"
        self.telephone = "15000000000"

    def allocId(self):
        self.id = User.nextId
        User.nextId += 1

    def insert(self):
        db.exec('''
            insert into user(id,hid,nickname,password,telephone) 
            values (?,?,?,?,?)
        ''', (self.id, self.hid, self.nickname, self.password, self.telephone))

    def read(self) -> bool:
        db.exec('''
            select hid,nickname,password,telephone 
            from user 
            where id=?
        ''', (self.id,))
        result = db.cursor.fetchone()
        if result is None:
            return False
        else:
            (self.hid, self.nickname, self.password, self.telephone) = result
            return True

    def write(self):
        db.exec('''
            update user
            set hid=?,nickname=?,password=?,telephone=?
            where id=?
        ''', (self.hid, self.nickname, self.password, self.telephone, self.id))

    def purchase(self, gid)->bool:
        goods = Goods(gid)
        if not goods.read():
            print("goods not found")
            return False
        if not goods.status == 'OnSale':
            print("goods is not onsale")
            return False
        if goods.uid == self.id:
            print("cannot purchase goods of yourself")
            return False
        goods.status = 'SoldOut'
        goods.write()
        db.exec('''
            insert into purchase(uid, gid, price)
            values (?,?,?)
        ''', (self.id, goods.id, goods.price))
        return True

    def remove(self, gid)->bool:
        goods = Goods(gid)
        if not goods.read():
            print("goods not found")
            return False
        if not goods.status == 'OnSale':
            print("goods is not onsale")
            return False
        if not goods.uid == self.id:
            print("cannot remove goods which not belong to you")
            return False
        goods.status = 'OffSale'
        return True

    def show(self):
        print(self.nickname, self.password, self.telephone)

    def getStatistics(self) -> (int, int, int):
        db.exec('''
            select on_sale_count, sold_count, purchased_count
            from statistics
            where uid = ?
        ''', (self.id, ))
        result = db.cursor.fetchone()
        return result

    
