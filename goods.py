from database import db
from myimage import defaultCoverId


class Goods:
    nextId = 0
    def __init__(self, _id = 0):
        self.id = _id
        self.uid = 0
        self.cid = defaultCoverId
        self.name = "名称五个字"
        self.price = 0.0
        self.status = "Unknown"
        self.description = "这是一段商品文字描述"


    @staticmethod
    def init():
        db.exec("select MAX(id) from goods")
        result = db.cursor.fetchone()
        if result[0] is not None:
            Goods.nextId = result[0] + 1

    @staticmethod
    def getOnSaleIdList(uid) -> list | None:
        db.exec('''
            select *
            from onsale_goods
            where uid <> ?
        ''', (uid, ))
        return db.cursor.fetchall()

    def allocId(self):
        self.id = Goods.nextId
        Goods.nextId += 1

    def insert(self):
        db.exec('''
            insert into goods(id, uid, cid, name, price, status, description)
            values (?,?,?,?,?,?,?)
        ''', (self.id, self.uid, self.cid, self.name, self.price, self.status, self.description))

    def read(self):
        db.exec('''
            select uid, cid, name, price, status, description
            from goods
            where id=?
        ''', (self.id,))
        result = db.cursor.fetchone()
        if result is None:
            return False
        else:
            (self.uid, self.cid, self.name, self.price, self.status, self.description) = result
            return True

    def write(self):
        db.exec('''
            update goods 
            set uid=?, cid=?, name=?, price=?, status=?, description=? 
            where id=?
        ''', (self.uid, self.cid, self.name, self.price, self.status, self.description, self.id))

    def show(self):
        print(self.id, self.name, self.status, self.description)