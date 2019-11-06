import requests
import json
from bs4 import BeautifulSoup  
import re 



def monitor(channel_id):
 
    new_vid = False
    url = 'https://www.youtube.com/feeds/videos.xml?channel_id={}'.format(channel_id)

    #gets the 14 most recent videos
    r = requests.get(url)
    if r.status_code == 200:
        x = BeautifulSoup(r.content, 'lxml')
        soup = x.find_all('id')
        lst = [_.text.split(':') for _ in soup]
        video_ids = [i[2] for i in lst if i[1] == 'video']

    
    #TODO: insert video ids in a file, and compare if new video id is added. if a new vid is added, grab id and send it to the 
    # comment_downloader script and delete last video id?
    
    
    print(video_ids)



   

  


    
    

if __name__ == "__main__":
    monitor('UCudNGAQXzpE1sMfoqPs67mQ')