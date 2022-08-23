from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
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
    0: '星期一',
    1: '星期二',
    2: '星期三',
    3: '星期四',
    4: '星期五',
    5: '星期六',
    6: '星期天',
}


def get_today_info():
    today = datetime.now().date()
    weekday = weekday_map[datetime.now().weekday()]
    from_weekend = 5 - datetime.now().weekday()
    return today, weekday, from_weekend


def get_weekday_info():
    info = None
    if datetime.now().weekday() in [0, 1, 2, 3, 4]:
        from_weekend = 5 - datetime.now().weekday()
        info = f'距离周末还剩{from_weekend}天'
    elif datetime.now().weekday() in [5, 6]:
        info = f'今天是周末，好好休息吧~'
    return info


def get_weather():
    url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
    res = requests.get(url).json()
    weather = res['data']['list'][0]
    print(weather)
    return weather['weather'], math.floor(weather['temp']), int(weather['low']), int(weather['high'])


def get_count():
    delta = today - datetime.strptime(start_date, "%Y-%m-%d")
    return delta.days


def get_birthday():
    next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
    if next < datetime.now():
        next = next.replace(year=next.year + 1)
    return (next - today).days


def get_words():
    words = requests.get("https://api.shadiao.pro/chp")
    if words.status_code != 200:
        return get_words()
    return words.json()['data']['text']


def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


def run():
    notes = '记得带纸~~'

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
    res = wm.send_template(user_id, template_id, data)
    print(res)


if __name__ == '__main__':
    run()
