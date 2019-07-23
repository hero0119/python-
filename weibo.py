#以爬取NBA新浪微博为例，爬取NBA微博对象url：https://m.weibo.cn/u/1883881851
import requests
from urllib.parse import urlencode
from pyquery import PyQuery as pq
from pymongo import MongoClient


base_url = 'https://m.weibo.cn/api/container/getIndex?'
headers = {
    'Host': 'm.weibo.cn',
    'Accept': 'application/json, text/plain, */*',
    'MWeibo-Pwa': '1',
    'Referer': 'https://m.weibo.cn/u/1883881851',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}
client = MongoClient()
db = client['weibo']
collection = db['weibo']

def get_page(page):
    params = {
        'type': 'uid',
        'value': '1883881851',
        'containerid': '1076031883881851',
        'page': page
    }
    url = base_url + urlencode(params)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json(), page
    except requests.ConnectionError as e:
        print('Error', e.args)


def parse_page(json, page: int):
    if json:
        items = json.get('data').get('cards')
        for index, item in enumerate(items):
            if page == 1 and index == 1:
                continue
            else:
                item = item.get('mblog', {})
                weibo = {}
                weibo['id'] = item.get('id')
                weibo['text'] = pq(item.get('text')).text()
                weibo['attitudes'] = item.get('attitudes_count')
                weibo['comments'] = item.get('comments_count')
                weibo['reposts'] = item.get('reposts_count')
                yield weibo


def save_to_mongo(result):
    if collection.insert(result):
        print('Saved to Mongo')


if __name__ == '__main__':
    for page in range(1,11):
        json = get_page(page)
        results = parse_page(*json)
        for result in results:
            print(result)
            save_to_mongo(result)
