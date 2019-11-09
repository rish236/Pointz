import requests
import json
from bs4 import BeautifulSoup  
import re 
import config
import pandas
import pymysql
import datetime
import time

def connect_db():
    conn = pymysql.connect(config.host, user=config.user,port=config.port,
                           passwd=config.password, db=config.dbname)

    conn.autocommit(True)
    return conn


def monitor(channel_id):
 
    new_vid = False
    url = 'https://www.youtube.com/feeds/videos.xml?channel_id={}'.format(channel_id)


    while new_vid == False:
        r = requests.get(url)
        if r.status_code == 200:
            x = BeautifulSoup(r.content, 'lxml')
            soup = x.find_all('id')
            lst = [_.text.split(':') for _ in soup]
            video_ids = [i[2] for i in lst if i[1] == 'video']
            ts = time.time()
            date_lst = [datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') for i in range(len(video_ids))]

            conn = connect_db()
            with conn:
                cursor = conn.cursor()
                query = "CREATE TABLE IF NOT EXISTS %s (id VARCHAR(20), date DATETIME, primary key(id))"%(channel_id)
                cursor.execute(query)


                cursor.execute("SELECT * FROM %s" %channel_id)
                rows = cursor.fetchall()
                # first time running -- inserts 14 most recent vids into database
                if not rows:
                    query = "INSERT INTO {} (id, date) VALUES (%s, %s)".format(channel_id)
                    data = [(a,b) for a,b in zip(video_ids, date_lst)]
                    cursor.executemany(query, data)
                # if not first time, compares xml to videos in database 
                else:   
                    db_lst = [rows[i][0] for i in range(len(rows))]
                    insert = set(video_ids).difference(db_lst)
                    date_lst = [datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') for i in range(len(insert))]
            
                    # if new video is found, insert into database
                    if insert:
                        query = "INSERT INTO {} (id, date) VALUES (%s, %s)".format(channel_id)
                        data = [(a,b) for a,b in zip(insert, date_lst)]
                        cursor.executemany(query, data)

                        new_vid = True
    #spawn new script 



if __name__ == "__main__":



    monitor('UCudNGAQXzpE1sMfoqPs67mQ')