import sys
import threading

import base64
import json
import urllib
import urllib2
import datetime
import pymongo
from pymongo import MongoClient

user_thread = []

user_pass = [
    {"user":"githublover001", "password": "qwe123456", "count": 0},
    {"user":"githublover002", "password": "qwe123456", "count": 0},
    {"user":"githublover003", "password": "qwe123456", "count": 0},
    {"user":"githublover004", "password": "qwe123456", "count": 0},
    {"user":"githublover005", "password": "qwe123456", "count": 0},
    {"user":"githublover006", "password": "qwe123456", "count": 0},
    {"user":"githublover007", "password": "qwe123456", "count": 0},
    {"user":"githublover008", "password": "qwe123456", "count": 0},
    {"user":"githublover009", "password": "qwe123456", "count": 0},
    {"user":"githublover010", "password": "qwe123456", "count": 0},
    {"user":"githublover011", "password": "qwe123456", "count": 0},
    {"user":"githublover012", "password": "qwe123456", "count": 0},
    {"user":"githublover013", "password": "qwe123456", "count": 0},
    {"user":"githublover014", "password": "qwe123456", "count": 0},
    {"user":"githublover015", "password": "qwe123456", "count": 0},
    {"user":"githublover016", "password": "qwe123456", "count": 0},
    {"user":"githublover017", "password": "qwe123456", "count": 0},
    {"user":"githublover018", "password": "qwe123456", "count": 0},
    {"user":"githublover019", "password": "qwe123456", "count": 0},
    {"user":"githublover020", "password": "qwe123456", "count": 0},
    {"user":"githublover021", "password": "qwe123456", "count": 0},
    {"user":"githublover022", "password": "qwe123456", "count": 0},
    {"user":"githublover023", "password": "qwe123456", "count": 0},
    {"user":"githublover024", "password": "qwe123456", "count": 0},
    {"user":"githublover025", "password": "qwe123456", "count": 0},
    {"user":"githublover026", "password": "qwe123456", "count": 0},
    {"user":"githublover027", "password": "qwe123456", "count": 0},
    {"user":"githublover028", "password": "qwe123456", "count": 0},
    {"user":"githublover029", "password": "qwe123456", "count": 0},
    {"user":"githublover030", "password": "qwe123456", "count": 0},
    {"user":"githublover031", "password": "qwe123456", "count": 0},
    {"user":"githublover032", "password": "qwe123456", "count": 0}
]

def init_db ():
    _db_addr = "127.0.0.1"
    _db_port = 27017
    _db_name = "github"

    client = MongoClient(_db_addr, _db_port)
    db = client[_db_name]
    return db

def get_free_user():
    min_count = 0
    i = 0
    for item in user_pass:
        if (item["count"] < user_pass[min_count]["count"]):
            min_count = i
        i += 1
    user_pass[min_count]["count"] += 1
    return min_count

# In github - follower, the default page_size is 30 and we cannot change it. 
#    seems...Correct me if I were wrong
def append_event(gh_user_id, page):
    url = "https://api.github.com/users/"+gh_user_id+"/events?page="+str(page);
    req = urllib2.Request(url)
    i = get_free_user()
    username = user_pass[i]["user"]
    password = user_pass[i]["password"]
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    req.add_header("Authorization", "Basic %s" % base64string)   

    res_data = urllib2.urlopen(req)
    res = res_data.read()

    val = json.loads(res)

    try:
        res_data = urllib2.urlopen(req)
    except urllib2.URLError, err:
# TODO we should note this ...
        print 'dliang url error'
        return []
    except urllib2.HTTPError, err:
        print '404 error'
        if err.code == 404:
             return []
    else:
        res = res_data.read()
        val = json.loads(res)
        return val

    print "How to get here?"
    return []

def upload_user_event(db, user_login):
    need_update = 0
# old res is in our db
    old_res = db["event"].find_one({"login": user_login})
    if old_res:
        return

    new_res = user_event_list(db, user_login)

    if len(new_res) == 0:
       return

    db["event"].insert({"login": user_login, "event": new_res})

def user_event_list(db, user_login):
    res = []
# 30 is github system defined
    i = 1
    while 1:
        ret_val = append_event(user_login, i)
        if len(ret_val) == 0:
            break
        res += ret_val
        i += 1

    return res

class myThread (threading.Thread):
    def __init__(self, db, start_id, end_id):
        threading.Thread.__init__(self)
        self.db = db
        self.start_id = start_id
        self.end_id = end_id
    def run(self):
        print "Starting " + str(self.start_id)
        i = self.start_id
        while i < self.end_id:
            dc = self.db["user"]
            result = dc.find_one({"id": i})
            if result:
                upload_user_event(self.db, result["login"])
            i += 1
        print "Exiting " + str(self.start_id)

def run_task():
    for item in user_thread:
        item.start()


def main():
    db = init_db()
    if db:
        #githublover001
        total = 10293416
        thread_num = 64
        gap = total/thread_num
        print gap

        for i in range(0, thread_num):
            start_id = i * gap
            if i == (thread_num - 1):
                end_id = total
            else:
                end_id = (i+1) * gap
            new_thread = myThread(db, start_id, end_id)
            user_thread.append(new_thread)
        run_task()

def fake():
    db = init_db()
    if db:
        total = 10293416
        thread_num = 64
        gap = total/thread_num
        print gap
        upload_user_event (db, "initlove")

main()
#fake()

