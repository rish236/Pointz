import os
import sys
import time
import json
import requests
import argparse
import lxml.html
import io
from lxml.cssselect import CSSSelector
import threading
import queue

class commentDownloader():
    def __init__(self):
        self.YOUTUBE_COMMENTS_URL = 'https://www.youtube.com/all_comments?v={youtube_id}'
        self.YOUTUBE_COMMENTS_AJAX_URL = 'https://www.youtube.com/comment_ajax'

        self.USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
        self.ret_cids = []

        self.first_iteration = True

        self.youtube_id = 'liniXxu3mIg'

        self.prev_page_token = None

        self.session = None

        self.session_token = None

        self.lock = threading.Lock()

        self.queue = queue.Queue()

    def find_value(self, html, key, num_chars=2):
        pos_begin = html.find(key) + len(key) + num_chars
        pos_end = html.find('"', pos_begin)

        return html[pos_begin: pos_end]


    def extract_comments(self, html):
        tree = lxml.html.fromstring(html)
        item_sel = CSSSelector('.comment-item')
        text_sel = CSSSelector('.comment-text-content')
        time_sel = CSSSelector('.time')
        author_sel = CSSSelector('.user-name')

        for item in item_sel(tree):
            yield {'cid': item.get('data-cid'),
                   'text': text_sel(item)[0].text_content(),
                   'time': time_sel(item)[0].text_content().strip(),
                   'author': author_sel(item)[0].text_content()}


    def ajax_request(self, url, params, data, retries=10, sleep=20):
        for _ in range(retries):
            response = self.session.post(url, params=params, data=data)
            if response.status_code == 200:
                response_dict = json.loads(response.text)
                return response_dict.get('page_token', None), response_dict['html_content']

            else:
                time.sleep(sleep)


    def first_request_call(self):
        session = requests.Session()
        session.headers['User-Agent'] = self.USER_AGENT

        response = session.get(self.YOUTUBE_COMMENTS_URL.format(youtube_id=self.youtube_id))

        html = response.text

        page_token = self.find_value(html, 'data-token')

        session_token = self.find_value(html, 'XSRF_TOKEN', 4)

        self.prev_page_token = page_token

        self.session = session

        self.session_token = session_token




    def ajax_thread_work(self):

        data = {'video_id': self.youtube_id,
                'session_token': self.session_token}

        params = {'action_load_comments': 1,
                  'order_by_time': True,
                  'filter': self.youtube_id}

        self.lock.acquire()
        if self.first_iteration:
            params['order_menu'] = True
        else:
            data['page_token'] = self.prev_page_token

        # Can take AJAX_URL out later
        response = self.ajax_request(self.YOUTUBE_COMMENTS_AJAX_URL, params, data)

        page_token, html = response
        self.queue.put(page_token)
        print("THIS IS THE PAGE TOKEN <-----------------", page_token)
        self.prev_page_token = page_token

        self.lock.release()


        self.first_iteration = False

        self.download_comments(html)



    def download_comments(self, html):
        for comment in self.extract_comments(html):
            if comment['cid'] not in self.ret_cids:
                self.ret_cids.append(comment['cid'])
                #print(comment)
                # yield comment

    def main(self):
        start_time = time.time()
        t_first = threading.Thread(target=self.first_request_call)
        t_first.start()
        t_first.join()
        #self.first_request_call()



        num_threads = 8
        threads = [0] * num_threads

        thread_response = 1

        # while thread_response is not None:
        #     for i in range(num_threads):
        #         threads[i] = threading.Thread(target=self.ajax_thread_work)
        #         threads[i].start()
        #         thread_response = self.queue.get()
        #         if thread_response is None:
        #             break
        #
        #     for i in range(num_threads):
        #         threads[i].join()

        for i in range(num_threads):
            threads[i] = threading.Thread(target=self.ajax_thread_work)
            threads[i].start()

        for i in range(num_threads):
            threads[i].join()
        print("TIME IT TAKESSSSSS------: ", time.time() - start_time)


if __name__ == "__main__":
    # test = ['-y', 'KnEpLGYS0SM', '-o', 'test.txt']
    # main(test)

    # download_comments_old('KnEpLGYS0SM')

    commentDownloader().main()


