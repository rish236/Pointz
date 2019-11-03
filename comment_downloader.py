import os
import sys
import time
import json
import requests
import argparse
import lxml.html
import io
from lxml.cssselect import CSSSelector
from multiprocessing import Pool

YOUTUBE_COMMENTS_URL = 'https://www.youtube.com/all_comments?v={youtube_id}'
YOUTUBE_COMMENTS_AJAX_URL = 'https://www.youtube.com/comment_ajax'

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
ret_cids = []

def find_value(html, key, num_chars=2):
    pos_begin = html.find(key) + len(key) + num_chars
    pos_end = html.find('"', pos_begin)

    return html[pos_begin: pos_end]


def extract_comments(html):
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


def ajax_request(session, url, params, data, retries=10, sleep=20):
    for _ in range(retries):
        response = session.post(url, params=params, data=data)
        if response.status_code == 200:
            response_dict = json.loads(response.text)
            return response_dict.get('page_token', None), response_dict['html_content']
            
        else:
            time.sleep(sleep)
def get_tokens_html():

    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    youtube_id =  'KnEpLGYS0SM'
    

    token_lst = []
    html_lst = []

    response = session.get(YOUTUBE_COMMENTS_URL.format(youtube_id=youtube_id))

    html = response.text

    page_token = find_value(html, 'data-token')
  
    session_token = find_value(html, 'XSRF_TOKEN', 4)
    first_iteration = True
    while page_token:
        data = {'video_id': youtube_id,
                'session_token': session_token}

        params = {'action_load_comments': 1,
                  'order_by_time': True,
                  'filter': youtube_id}

        if first_iteration:
            params['order_menu'] = True
        else:
            data['page_token'] = page_token

        response = ajax_request(session, YOUTUBE_COMMENTS_AJAX_URL, params, data)
       

        page_token, html = response
        token_lst.append(page_token)
        html_lst.append(html)
        first_iteration = False
    return token_lst, html_lst


def download_comments(token, html):

    for comment in extract_comments(html):
        if comment['cid'] not in ret_cids:
            ret_cids.append(comment['cid'])
            print(comment)
            x+=1
            #yield comment


# def main(argv):
#     parser = argparse.ArgumentParser(add_help=False, description=('Download Youtube comments without using the Youtube API'))
#     parser.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS, help='Show this help message and exit')
#     parser.add_argument('--youtubeid', '-y', help='ID of Youtube video for which to download the comments')
#     parser.add_argument('--output', '-o', help='Output filename (output format is line delimited JSON)')
#     parser.add_argument('--limit', '-l', type=int, help='Limit the number of comments')

#     try:
#         args = parser.parse_args(argv)

#         youtube_id = args.youtubeid
#         output = args.output
#         limit = args.limit

#         if not youtube_id or not output:
#             parser.print_usage()
#             raise ValueError('you need to specify a Youtube ID and an output filename')

#         print('Downloading Youtube comments for video:', youtube_id)
#         count = 0
#         with io.open(output, 'w', encoding='utf8') as fp:
#             for comment in download_comments(youtube_id):
#                 comment_json = json.dumps(comment, ensure_ascii=False)
#                 print(comment_json.decode('utf-8') if isinstance(comment_json, bytes) else comment_json, file=fp)
#                 count += 1
#                 sys.stdout.write('Downloaded %d comment(s)\r' % count)
#                 sys.stdout.flush()
#                 if limit and count >= limit:
#                     break
#         print('\nDone!')


    # except Exception as e:
    #     print('Error:', str(e))
    #     sys.exit(1)


if __name__ == "__main__":
    # test = ['-y', 'KnEpLGYS0SM', '-o', 'test.txt']
    # main(test)


    #download_comments_old('KnEpLGYS0SM')

    token, html = get_tokens_html()
    # pool = Pool(4)
    # pool.starmap(download_comments, zip(token,html))
    # pool.close()
    # pool.join()
   
    
   
    

