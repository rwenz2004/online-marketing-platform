import remote

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
        result = remote.get_max_id("message")
        if result is not None:
            Message.nextId = result + 1
        else:
            exit(-1)

    def allocId(self):
        self.id = Message.nextId
        Message.nextId += 1

    def insert(self):
        remote.insert_message(self.id, self.sender, self.receiver, self.content, self.type)
        
    def read(self) -> bool:
        result = remote.get_message(self.id)
        if result is not None:
            self.sender, self.receiver, self.content, self.type = result
            return True
        else:
            return False

    def write(self):
        remote.set_message(self.id, self.sender, self.receiver, self.content, self.type)

