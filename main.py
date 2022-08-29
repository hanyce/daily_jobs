from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
from retrying import retry
import requests
import os
import random

today = datetime.now()
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]

weekday_map = {
    0: '星期二&&4',
    1: '星期三&&3',
    2: '星期四&&2',
    3: '星期五&&1',
    4: '星期六',
    5: '星期天',
    6: '星期一&&5',
}


def get_today_info():
    today = datetime.now().date()
    weekday = weekday_map[datetime.now().weekday()].split('&&')[0]
    from_weekend = 5 - datetime.now().weekday()
    return today, weekday, from_weekend


def get_weekday_info():
    info = None
    _weekday = datetime.now().weekday()
    if _weekday in [6, 0, 1, 2, 3]:
        from_weekend = weekday_map[_weekday].split('&&')[1]
        info = f'距离周末还剩{from_weekend}天'
    elif _weekday in [4, 5]:
        info = '今天是周末，好好休息吧~'
    return info


def get_weather():
    url = f"http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city={city}"
    res = requests.get(url).json()
    weather = res['data']['list'][0]
    return weather['weather'], math.floor(weather['temp']), int(weather['low']), int(weather['high'])


def get_count():
    delta = today - datetime.strptime(start_date, "%Y-%m-%d")
    return delta.days


def get_birthday():
    next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
    if next < datetime.now():
        next = next.replace(year=next.year + 1)
    return (next - today).days


@retry()
def get_words():
    words = requests.get("https://api.shadiao.pro/chp")
    return words.json()['data']['text']


def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


def run():
    notes = ''

    client = WeChatClient(app_id, app_secret)

    wm = WeChatMessage(client)
    today_date, weekday, from_weekend = get_today_info()
    wea, temperature, low, high = get_weather()

    data = {
        "today_info": {
            "value": f'{weekday}',
            "color": "#FF44AA"
        },
        "from_weekend": {
            "value": get_weekday_info(),
        },
        "weather": {
            "value": wea
        },
        "low": {
            "value": low,
            "color": "#008000"
        },
        "high": {
            "value": high,
            "color": "#FF0000"
        },
        "birthday_left": {
            "value": get_birthday()
        },
        "words": {
            "value": f'{get_words()} \n {notes}',
            "color": get_random_color()
        }
    }
    print(data)
    res = wm.send_template(user_id, template_id, data)
    print(res)


if __name__ == '__main__':
    run()
