from flask import Flask, request, jsonify
from database import db

app = Flask(__name__)

def database_init():
    try:
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
        print("Database initialized successfully.")
    except Exception as e:
        print(e)
        exit(-1)

@app.route('/maxid', methods=['GET'])
def get_max_id():
    try:
        type = request.args.get('type')
        if not type:
            raise Exception("type is required")
        db.exec(f"select MAX(id) from {type}")
        result = db.cursor.fetchone()
        if result[0] is not None:
            return jsonify(result[0])
        else:
            return jsonify(-1)
    except Exception as e:
        return jsonify({"error": f"Server Error: {e}"}), 400

@app.route('/insert_image', methods=['POST'])
def insert_image():
    try:
        id = request.form.get('id')
        data = request.files['data'].read()
        db.exec('''
            insert into image(id, data)
            values (?,?)
        ''', (id, data))
        return jsonify({"message": "Image inserted successfully"})
    except Exception as e:
        return jsonify({"error": f"Server Error: {e}"}), 400

@app.route('/get_image', methods=['POST'])
def get_image():
    try:
        id = request.form.get('id')
        db.exec('''
            select data
            from image
            where id = ?
        ''', (id,))
        result = db.cursor.fetchone()
        if result[0] is not None:
            return result[0]
        else:
            return jsonify({"error": "Image not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Server Error: {e}"}), 400
    
@app.route('/set_image', methods=['POST'])
def set_image():
    try:
        id = request.form.get('id')
        data = request.files['data'].read()
        db.exec('''
            update image
            set data = ?
            where id = ?
        ''', (data, id))
        return jsonify({"message": "Image updated successfully"})
    except Exception as e:
        return jsonify({"error": f"Server Error: {e}"}), 400

@app.route('/insert_message', methods=['POST'])
def insert_message():
    try:
        id = request.form.get('id')
        sender = request.form.get('sender')
        receiver = request.form.get('receiver')
        content = request.form.get('content')
        type = request.form.get('type')
        db.exec('''
            insert into message(id, sender, receiver, content, type)
            values (?,?,?,?,?)
        ''', (id, sender, receiver, content, type))
        return jsonify({"message": "Message inserted successfully"})
    except Exception as e:
        return jsonify({"error": f"Server Error: {e}"}), 400
    
@app.route('/get_message', methods=['POST'])
def get_message():
    try:
        id = request.form.get('id')
        db.exec('''
            select sender, receiver, content, type
            from message
            where id = ?
        ''', (id,))
        result = db.cursor.fetchone()
        if result is not None:
            return jsonify(result)
        else:
            return jsonify({"error": "Message not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Server Error: {e}"}), 400
    
@app.route('/set_message', methods=['POST'])
def set_message():
    try:
        id = request.form.get('id')
        sender = request.form.get('sender')
        receiver = request.form.get('receiver')
        content = request.form.get('content')
        type = request.form.get('type')
        db.exec('''
            update message
            set sender=?, receiver=?, content=?, type=?
            where id=?
        ''', (sender, receiver, content, type, id))
        return jsonify({"message": "Message updated successfully"})
    except Exception as e:
        return jsonify({"error": f"Server Error: {e}"}), 400

@app.route('/existed_user', methods=['GET'])
def existed_user():
    try:
        id = request.args.get('id')
        db.exec('''
            select id
            from user
            where id = ?
        ''', (id,))
        if db.cursor.fetchone() is None:
            return jsonify({"exists": False})
        return jsonify({"exists": True})
    except Exception as e:
        return jsonify({"error": f"Server Error: {e}"}), 400

@app.route('/existed_telephone', methods=['GET'])
def existed_telephone():
    try:
        telephone = request.args.get('telephone')
        db.exec('''
            select id
            from user
            where telephone like ?
        ''', (telephone,))
        if db.cursor.fetchone() is None:
            return jsonify({"exists": False})
        return jsonify({"exists": True})
    except Exception as e:
        return jsonify({"error": f"Server Error: {e}"}), 400

@app.route('/insert_user', methods=['POST'])
def insert_user():
    try:
        id = request.form.get('id')
        hid = request.form.get('hid')
        nickname = request.form.get('nickname')
        password = request.form.get('password')
        telephone = request.form.get('telephone')
        db.exec('''
            insert into user(id, hid, nickname, password, telephone)
            values (?,?,?,?,?)
        ''', (id, hid, nickname, password, telephone))
        return jsonify({"message": "User inserted successfully"})
    except Exception as e:
        return jsonify({"error": f"Server Error: {e}"}), 400

@app.route('/get_user', methods=['POST'])
def get_user():
    try:
        id = request.form.get('id')
        db.exec('''
            select hid, nickname, password, telephone
            from user
            where id = ?
        ''', (id,))
        result = db.cursor.fetchone()
        if result is not None:
            return jsonify(result)
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Server Error: {e}"}), 400

@app.route('/set_user', methods=['POST'])
def set_user():
    try:
        id = request.form.get('id')
        hid = request.form.get('hid')
        nickname = request.form.get('nickname')
        password = request.form.get('password')
        telephone = request.form.get('telephone')
        db.exec('''
            update user
            set hid=?, nickname=?, password=?, telephone=?
            where id=?
        ''', (hid, nickname, password, telephone, id))
        return jsonify({"message": "User updated successfully"})
    except Exception as e:
        return jsonify({"error": f"Server Error: {e}"}), 400

if __name__ == '__main__':
    database_init()
    app.run(host='0.0.0.0', port=5000)