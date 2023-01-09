import pandas as pd
import requests
import json
from base64 import b64encode as b64

with open('./server/username_to_user_id.py') as f:
    data = f.read()

old_names = json.loads(data)

def encoder(s_ascii = "bhollan"):
    s_code = b64(s_ascii.encode("utf-8")).decode("utf-8")
    s_code = s_code.replace("=", "")
    s_code = s_code.replace("+", "")
    s_code = s_code.replace("\/", "_")
    return s_code

ratings_url = "https://acquire.tlstyer.com/stats/data/ratings.json"

player_page = "https://acquire.tlstyer.com/stats/data/users/YmhvbGxhbg.json"

resp = requests.get(ratings_url)



