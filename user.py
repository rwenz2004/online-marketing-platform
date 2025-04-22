import remote
from goods import Goods
from myimage import defaultPhotoId


class User:
    #静态属性
    nextId = 10000

    #静态方法
    @staticmethod
    def init():
        result = remote.get_max_id("user")
        if result is not None:
            User.nextId = result + 1
        else:
            exit(-1)

    @staticmethod
    def existedId(_id) -> bool:
        result = remote.existed_user(_id)
        if result is not None:
            return True
        else:
            return False

    @staticmethod
    def existedTelephone(telephone) -> bool:
        result = remote.existed_telephone(telephone)
        if result is not None:
            return True
        else:
            return False

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
        remote.insert_user(self.id, self.hid, self.nickname, self.password, self.telephone)

    def read(self) -> bool:
        result = remote.get_user(self.id)
        if result is not None:
            self.hid, self.nickname, self.password, self.telephone = result
            return True
        else:
            return False
        
    def write(self):
        remote.set_user(self.id, self.hid, self.nickname, self.password, self.telephone)

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
        return remote.purchase(self.id, gid, goods.price)

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

    
