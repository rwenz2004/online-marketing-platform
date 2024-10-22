from database import db


class Chat:
    chats = []
    def __init__(self, host=0, custom=0):
        self.host = host
        self.custom = custom
        self.messages = []

    @staticmethod
    def refreshChats():
        Chat.chats.clear()
        db.exec('''
            select
                *
            from
                chat
        ''')
        for row in db.cursor.fetchall():
            id1, id2 = str(row[0]).split('-')
            Chat.chats.append((int(id1), int(id2)))

    @staticmethod
    def getChats(uid) -> []:
        chats = []
        for row in Chat.chats:
            if row[0] == uid:
                chats.append(row[1])
            if row[1] == uid:
                chats.append(row[0])
        return chats

    def readMessages(self):
        db.exec('''
            select
                sender, content, type, time
            from
                message
            where
                (sender = ? and receiver = ?) or (sender = ? and receiver = ?)
            order by
                time
        ''', (self.host, self.custom, self.custom, self.host))
        self.messages = db.cursor.fetchall()

    def insert(self, content, _type):
        db.exec('''
            insert into
                message(sender, receiver, content, type)
            values
                (?,?,?,?)
        ''', (self.host, self.custom, content, _type))

if __name__ == '__main__':
    pass