# -*- coding: utf-8 -*-
"""
XmasGame

Contains information and methods related to XmasGame

Created on Fri Dec 21 18:20:37 2018

@author: chuny
"""

import numpy
import matplotlib.pyplot as plt
import csv
import time
import datetime
import json
import requests

    
## class definitions
class Player:
    fullname = 'John Doe' # full name
    name   = 'John'      # first name
    nm     = 'J'         # shortened name
    color  = '#000000'   # RGB string
    times  = time.time() # time stamps
    points = 0           # points at time stamps
    
    
    def __init__(self,fullname,name,nm,color,t0,p0):
        self.fullname = fullname
        self.name   = name
        self.nm     = nm
        self.color  = color
        self.times  = [t0]
        self.points = [p0]
        
        
    def point_change(self,t,dp):
        self.times.append(t)
        self.points.append(self.points[-1]+dp)
        
    def point_at_time(self,t):
        for ii in numpy.arange(len(self.times)):
            if self.times[ii] > t:
                return self.points[ii-1]
            
    def legend_str(self):
        return self.name + " (" + str(int(self.points[-1])) + ")"
            
    def plot_progress(self,currTime):
        tp = [self.times[0]]
        pp = [self.points[0]]
        
        for ii in numpy.arange(1,len(self.times)):
            tp.append(self.times[ii])
            tp.append(self.times[ii])
            
            pp.append(self.points[ii-1])
            pp.append(self.points[ii])
        
        tp.append(currTime)
        pp.append(self.points[-1])
        
        tp[:] = [(t - t0)/86400  for t in tp]
        plt.plot([tp[-1],(tf-t0)/86400],[self.points[-1],self.points[-1]],color=self.color,linestyle='--')
        hhh, = plt.plot(tp,pp,color=self.color,linewidth=3)
        return hhh

def find_player(name):
    for ii in numpy.arange(len(players)):
        if players[ii].fullname == name:
            return ii
    
        

# =============================================================================
# constants/parameters
# =============================================================================
# game settings
year = 2018   # year of the game
timezone = -6 # adjustment from UTC (CST = -6)
first_penalty = 3 # points for hearing it first
point_norm = 1 # normal point per hit


# important times for game
# starting time
t0 = time.mktime(time.strptime(str(year)+"/12/01","%Y/%m/%d")) + timezone*3600

# ending time
tf = time.mktime(time.strptime(str(year)+"/12/26","%Y/%m/%d")) + timezone*3600

# bonus time
tb = time.mktime(time.strptime(str(year)+"/12/25","%Y/%m/%d")) + timezone*3600


# =============================================================================
# Pre-existing information
# =============================================================================

## players
players = []
# read in the list of players
with open("players.txt") as player_file:
    csv_reader = csv.reader(player_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        players.append(Player(row[0],row[1],row[2],row[3],float(row[4]),float(row[5])))


## point changes
# read in the points
t_last_hit = t0
pts = first_penalty+1
with open("record.txt") as record_file:
    csv_reader = csv.reader(record_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        i_player = find_player(row[0])
        t_hit = float(row[1])
        if t_hit > t_last_hit:
            pts = max(1,pts-1)
            t_last_hit = t_hit
        
        players[i_player].point_change(float(row[1]),pts)   
        
        
# =============================================================================
# GroupMe bot setups
# =============================================================================
        
# IDs, don't let anyone see this!
token = "69abb1c0e7600136b98842666b04d6d4"
bot_id = "c2ee171e35788b9621d9c57c28"
group_id = "46392787"


# code that doesn't change
url_group = "https://api.groupme.com/v3/groups"

url_img = "https://image.groupme.com/pictures"
head_img = {"X-Access-Token": token, "content-type": "image/png"}

url_msg = "https://api.groupme.com/v3/bots/post"
head_msg = {"content-type": "application/json", "Accept-Charset": "UTF-8"}

msg_data = {}
msg_data["bot_id"] = bot_id
msg_data["text"] = "Testing"
msg_json = json.dumps(msg_data)



# =============================================================================
# Things to actual run in real time
# =============================================================================
keep_running = True

msg_data["text"] = "Hello, everyone! This is the friendly game management bot!\nTo record hearing the song, start your message with '!hit'"
msg_json = json.dumps(msg_data)
req_msg = requests.post(url_msg, data=msg_json, headers = head_msg)
        
# last message before the bot is activated
req_chat = requests.get(url_group + "/" + group_id + "?token=" + token)
last_msg = req_chat.json()["response"]["messages"]["preview"]["text"]
t_last_msg = req_chat.json()["response"]["messages"]["last_message_created_at"]

while keep_running:
    # an output to make sure the program is running
    currTime = time.time() + timezone*3600
    currTime_utc = datetime.datetime.utcfromtimestamp(currTime)
    print(str(currTime)+" ("+str(currTime_utc)+")")
    
    if currTime > tb and point_norm == 1:
        point_norm = 2
        img= open("double_point_announcement.png","rb")
        req_img = requests.post(url_img,data=img.read(),headers=head_img)
        url_pic = req_img.json()["payload"]["url"]
        attach = {}
        attach["type"] = "image"
        attach["url"] = url_pic
        msg_data["attachments"] = [attach]
        msg_data["text"] = "The Mariah Carey Merry Christmas Bonus period has started! From now on, you get two points for hearing the song!"
        msg_json = json.dumps(msg_data)
        req_msg = requests.post(url_msg, data=msg_json, headers = head_msg)
        
        
    
    try:
        # get the last message
        req_chat = requests.get(url_group + "/" + group_id + "?token=" + token)
        last_msg = req_chat.json()["response"]["messages"]["preview"]["text"]
        t_this_msg = req_chat.json()["response"]["messages"]["last_message_created_at"]
        
        # if this message is new...
        if t_last_msg < t_this_msg:
            t_last_msg = t_this_msg+5
            
            # test if the message starts with '!hit'
            if last_msg.startswith('!hit'):
                name = req_chat.json()["response"]["messages"]["preview"]["nickname"]
                
                i_player = find_player(name)
                if t_this_msg > t_last_hit:
                    pts = max(point_norm,pts-1)
                    t_last_hit = t_this_msg
                
                players[i_player].point_change(t_this_msg,pts)  
                
                f = open("record.txt","a")
                f.write(name+","+str(t_this_msg)+"\n")
                f.flush()
                
            # plot result
            plt.close()
            p4l = []    # plot for legends
            leg = []    # legends
            
            for ii in numpy.arange(len(players)):
                p4l.append(players[ii].plot_progress(currTime))
                leg.append(players[ii].legend_str())
                
            plt.legend(p4l ,leg, loc='center left', bbox_to_anchor=(1, 0.5))
            plt.grid()
            
            plt.savefig(fname="progress1.png",format="png")
            
            # send the new message
            text = ""
            for ii in numpy.arange(len(players)):
                text = text + ", " + players[ii].legend_str()
            
            
            img= open("progress1.png","rb")
            req_img = requests.post(url_img,data=img.read(),headers=head_img)
            url_pic = req_img.json()["payload"]["url"]
            
            attach = {}
            attach["type"] = "image"
            attach["url"] = url_pic
            msg_data["attachments"] = [attach]
            msg_data["text"] = text
            msg_json = json.dumps(msg_data)
            
            req_msg = requests.post(url_msg, data=msg_json, headers = head_msg)
            print(req_msg)
    except KeyboardInterrupt:
        print("KeyboardInterrupt detected!")
        msg_data["text"] = "I'm going to sleep now.... *YAWN* (The bot has been stopped temporaily)"
        msg_data["attachments"] = []
        msg_json = json.dumps(msg_data)
        req_msg = requests.post(url_msg, data=msg_json, headers = head_msg)
        
        keep_running = False
    except Exception as ex:
        print("some error occurred")
        msg_data["text"] = "Beep beep! Some error occurred when recording this! Manual entry might be necessary.\nException: "+str(ex)
        msg_data["attachments"] = []
        msg_json = json.dumps(msg_data)
        req_msg = requests.post(url_msg, data=msg_json, headers = head_msg)
        
        
        