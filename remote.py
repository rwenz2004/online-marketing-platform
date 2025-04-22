from unittest import result
from urllib import response
import requests

url = "http://localhost:5000"

def get_max_id(type="goods"):
    response = requests.get(
        url + "/maxid",
        params={
            "type": type
        }
    )
    if response.status_code == 200:
        return int(response.text)
    else:
        print(response.text)
        return None
    
def insert_image(id, data):
    response = requests.post(
        url + "/insert_image",
        params={
            "id": id,
            "data": data
        }
    )
    if response.status_code == 200:
        return True
    else:
        print(response.text)
        return False

def get_image(id):
    response = requests.post(
        url + "/get_image",
        params={
            "id": id
        }
    )
    if response.status_code == 200:
        return response.content
    else:
        print(response.text)
        return None

def set_image(id, data):
    response = requests.post(
        url + "/set_image",
        params={
            "id": id,
            "data": data
        }
    )
    if response.status_code == 200:
        return True
    else:
        print(response.text)
        return False
    
def insert_message(id, sender, receiver, content, type):
    response = requests.post(
        url + "/insert_message",
        params={
            "id": id,
            "sender": sender,
            "receiver": receiver,
            "content": content,
            "type": type
        }
    )
    if response.status_code == 200:
        return True
    else:
        print(response.text)
        return False
    
def get_message(id):
    response = requests.post(
        url + "/get_message",
        params={
            "id": id
        }
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(response.text)
        return None

def set_message(id, sender, receiver, content, type):
    response = requests.post(
        url + "/set_message",
        params={
            "id": id,
            "sender": sender,
            "receiver": receiver,
            "content": content,
            "type": type
        }
    )
    if response.status_code == 200:
        return True
    else:
        print(response.text)
        return False

def existed_user(id):
    response = requests.get(
        url + "/existed_user",
        params={
            "id": id
        }
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(response.text)
        return None
    
def existed_telephone(telephone):
    response = requests.get(
        url + "/existed_telephone",
        params={
            "telephone": telephone
        }
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(response.text)
        return None

def insert_user(id, hid, nickname, password, telephone):
    response = requests.post(
        url + "/insert_user",
        params={
            "id": id,
            "hid": hid,
            "nickname": nickname,
            "password": password,
            "telephone": telephone
        }
    )
    if response.status_code == 200:
        return True
    else:
        print(response.text)
        return False

def get_user(id):
    response = requests.post(
        url + "/get_user",
        params={
            "id": id
        }
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(response.text)
        return None
    
def set_user(id, hid, nickname, password, telephone):
    response = requests.post(
        url + "/set_user",
        params={
            "id": id,
            "hid": hid,
            "nickname": nickname,
            "password": password,
            "telephone": telephone
        }
    )
    if response.status_code == 200:
        return True
    else:
        print(response.text)
        return False
    
def purchase(uid, gid, price):
    response = requests.post(
        url + "/purchase",
        params={
            "uid": uid,
            "gid": gid,
            "price": price
        }
    )
    if response.status_code == 200:
        return True
    else:
        print(response.text)
        return False

