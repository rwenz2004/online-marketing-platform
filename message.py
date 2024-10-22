from database import db


class Message:
    nextId = 0
    def __init__(self):
        self.id = 0
        self.sender = 0
        self.receiver = 0
        self.content = ""
        self.type = "text"

    @staticmethod
    def init():
        db.exec('''
            select
                MAX(id)
            from
                message
        ''')
        result = db.cursor.fetchone()
        if result[0] is not None:
            Message.nextId = result[0] + 1

    def allocId(self):
        self.id = Message.nextId
        Message.nextId += 1

    def insert(self):
        db.exec('''
            insert into
            message(id, sender, receiver, content, type)
            values (?,?,?,?,?)
        ''', (self.id, self.sender, self.receiver, self.content, self.type))

    def read(self) -> bool:
        db.exec('''
            select
                sender, receiver, content, type
            from
                message
            where
                id = ?
        ''', (self.id,))
        result = db.cursor.fetchone()
        if result is None:
            return False
        else:
            (self.sender, self.receiver, self.content, self.type) = result
            return True

    def write(self):
        db.exec('''
            update
                message
            set
                sender=?, receiver=?, content=?, type=?
            where
                id=?
        ''', (self.sender, self.receiver, self.content, self.type, self.id))

