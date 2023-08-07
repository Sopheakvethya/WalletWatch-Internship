import psycopg2

class Database:
    def __init__(self, database, user, password, host, port):
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def init(self):
        try:
            self.conn = psycopg2.connect(
                database=self.database,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
        except Exception as e:
            raise Exception("Cannot connect to database\n", e)

        self.cur = self.conn.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS items
                (ID     INT     PRIMARY KEY NOT NULL,
                name    TEXT                NOT NULL,
                price   INT                 NOT NULL);""")
        
        self.conn.commit()

    def insert(self, item_id, item_name, item_price):
        self.cur.execute("INSERT INTO items VALUES (%s, %s, %s);", (item_id, item_name, item_price))
        self.conn.commit()

    def delete(self, item_id):
        self.cur.execute("DELETE FROM items WHERE id=%s", (item_id))
        self.conn.commit()

    def get_items(self):
        self.cur.execute("SELECT * FROM items")
        return self.cur.fetchall()
    
    def total_spending(self):
        self.cur.execute("SELECT SUM(price) FROM items;")
        return self.cur.fetchone()
    
    def close_db(self):
        self.conn.close()