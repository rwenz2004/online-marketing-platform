import remote
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
        result = remote.get_max_id("goods")
        if result is not None:
            print(f"max goods id: {result}")
            Goods.nextId = result + 1

    @staticmethod
    def getOnSaleIdList(uid) -> list | None:
        db.exec('''
            select *
            from onsale_goods
            where uid <> ?
        ''', (uid, ))
        return db.cursor.fetchall()

    @staticmethod
    def getGoodsListSatisfy(uid, status = "%") -> list:
        if status == "Bought":
            return Goods.getBoughtGoodsList(uid)
        db.exec('''
            select id
            from goods
            where uid=? and status like ?
        ''', (uid, status))
        result = db.cursor.fetchall()
        ret = []
        for i in result:
            ret.append(i[0])
        return ret

    @staticmethod
    def getBoughtGoodsList(uid) -> list:
        db.exec('''
                select gid
                from purchase
                where uid=?
            ''', (uid,))
        result = db.cursor.fetchall()
        ret = []
        for i in result:
            ret.append(i[0])
        return ret

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

    def getCreateTime(self):
        db.exec('''
            select time
            from goods
            where id=?
        ''', (self.id,))
        result = db.cursor.fetchone()
        if result is None:
            return None
        else:
            return result[0]

    @staticmethod
    def blurSearch(uid, text) -> list:
        print("text:", text)
        result = []
        if len(text) > 0:
            db.exec('''
                        SELECT g.id
                        FROM goods g
                        JOIN user u ON g.uid = u.id
                        WHERE g.name LIKE '%?%' OR u.nickname LIKE '%?%';
                    ''', (text, text))
            result = db.cursor.fetchall()
        else:
            result = Goods.getOnSaleIdList(uid)
        ret = []
        for i in result:
            ret.append(i[0])
        return ret