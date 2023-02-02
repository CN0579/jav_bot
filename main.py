import bs4
import requests

jav_cookie = 'existmag=mag; PHPSESSID=cmiqrmbfnj59jg32ddr3ivc5e7'
ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.61'
proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}


def str_cookies_to_dict(cookies):
    dict_cookie = {}
    str_cookie_list = cookies.split(';')
    for cookie in str_cookie_list:
        if cookie.strip(' '):
            cookie_key_value = cookie.split('=')
            if len(cookie_key_value) < 2:
                continue
            key = cookie_key_value[0]
            value = cookie_key_value[1]
            dict_cookie[key] = value
    return dict_cookie


def grab_jav_bus(actor_name):
    url = f"https://www.javbus.com/searchstar/{actor_name}"
    cookie_dict = str_cookies_to_dict(jav_cookie)
    headers = {'cookie': jav_cookie, 'Referer': "https://www.javlibrary.com"}
    if ua:
        headers['User-Agent'] = ua
    res = requests.get(url=url, proxies=proxies, cookies=cookie_dict, headers=headers)
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    actors = soup.select('a.avatar-box')
    if len(actors)>1:
        print("搜索出了多个演员,请输入更为详细的演员艺名")
        return None
    if len(actors)<1:
        print("演员艺名错误")
        return None
    actor_url = actors[0].get('href')
    return actor_url


def grab_actor(actor_url):
    cookie_dict = str_cookies_to_dict(jav_cookie)
    headers = {'cookie': jav_cookie, 'Referer': "https://www.javlibrary.com"}
    if ua:
        headers['User-Agent'] = ua
    res = requests.get(url=actor_url, proxies=proxies, cookies=cookie_dict, headers=headers)
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    list = soup.select('a.movie-box')
    for item in list:
        date_list = item.select('date')

        print(f"上映时间:{date_list[1].text},番号:{date_list[0].text}")


if __name__ == '__main__':
    actor_url = grab_jav_bus('八掛うみ')
    if actor_url:
        print('八掛うみ')
        grab_actor(actor_url)
