import config
import requests
from requests_oauthlib import OAuth1
import json
import ast

target = "theweeknd"
source = "shaden78343862"


url = 'https://api.twitter.com/1.1/friendships/show.json?source_screen_name=%s&target_screen_name=%s'%(source, target)

auth = OAuth1(config.twitter_consumer, config.twitter_consumer_secret, config.twitter_access, config.twitter_access_secret)
r = requests.get(url, auth=auth).json()


s = str(r.values()).replace("'", '"').split(', "target')
new = s[0].replace('dict_values([{"source": ', "").replace("}])", "")

my_dict = ast.literal_eval(new)
for k,v in my_dict.items():
    if k == "following":
        print(v)