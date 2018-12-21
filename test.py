# -*- coding: utf-8 -*-
"""
Created on Fri Dec 21 09:11:58 2018

@author: chuny
"""

import requests
import json

# IDs, don't let anyone see this!
token = "69abb1c0e7600136b98842666b04d6d4"
bot_id = "c2ee171e35788b9621d9c57c28"




## meat of the code


url_img = "https://image.groupme.com/pictures"
head_img = {"X-Access-Token": token, "content-type": "image/png"}
img= open("progress.png","rb")
req_img = requests.post(url_img,data=img.read(),headers=head_img)
print(req_img)
url_img = req_img.json()["payload"]["url"]
print(url_img)

data = {}
data["bot_id"] = bot_id
data["text"] = "What is love?"
attach = {}
attach["type"] = "image"
attach["url"] = url_img
data["attachments"] = [attach]
json_data = json.dumps(data)

print(json_data)

url_bot = "https://api.groupme.com/v3/bots/post"
head_bot = {"content-type": "application/json", "Accept-Charset": "UTF-8"}
req_post = requests.post(url_bot, data=json_data, headers = head_bot)
print(req_post)
