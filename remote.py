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