import sqlite3

class Database:
    def __init__(self):
        self.connection = sqlite3.connect('omp.db', check_same_thread=False)
        self.cursor = self.connection.cursor()

    def exec(self, *args, **kwargs):
        self.cursor.execute( *args, **kwargs)
        self.connection.commit()

db = Database()


