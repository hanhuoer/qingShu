import re
from xml.sax.saxutils import unescape

import requests
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import mock.conf.user_conf as conf
import json

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 1000)

user_class_info = {}

user_info = {}

user_cookies = {}

headers = {
        'Host': "degree.qingshuxuetang.com",
        'Connection': "keep-alive",
        'Pragma': "no-cache",
        'Cache-Control': "no-cache",
        'Accept': "application/json",
        'Origin': "https://degree.qingshuxuetang.com",
        'X-Requested-With': "XMLHttpRequest",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        'Content-Type': "application/json",
        'Referer': "https://degree.qingshuxuetang.com/hngd/Student/CourseShow?courseId=1298&teachPlanId=271&periodId=11&cw_nodeId=kcjs_1",
        'Accept-Encoding': "gzip, deflate, br",
        'Accept-Language': "zh-CN,zh;q=0.9,ja;q=0.8,ko;q=0.7,en;q=0.6",
        'cache-control': "no-cache"
    }


def login(username, password):
    browser.get('https://degree.qingshuxuetang.com/hngd/Home')

    username_input = wait.until(
        EC.presence_of_element_located((By.ID, 'uname'))
    )

    username_input.clear()
    username_input.send_keys(username)

    password_input = wait.until(
        EC.presence_of_element_located((By.ID, 'pwd'))
    )

    password_input.clear()
    password_input.send_keys(password)

    login_button = wait.until(
        EC.presence_of_element_located((By.ID, 'loginBtn'))
    )

    login_button.click()


def init_cookies():
    cookies = browser.get_cookies()

    print(cookies)
    for cookie in cookies:
        user_cookies.setdefault(cookie['name'], cookie['value'])

    return user_cookies


def get_cookies():
    cookies = ''

    for cookie in user_cookies:
        cookies += cookie + '=' + user_cookies[cookie] + '; '

    return cookies


def init_user_info():
    global user_info

    init_s = re.findall('Behavior\.init\((.*?)\);', browser.page_source, re.S)[0]

    user_info = {
        'college': re.findall('college.*?\'(.*?)\',', init_s, re.S)[0],
        'schoolId': re.findall('schoolId:.(.*?),', init_s, re.S)[0],
        'userId': re.findall('userId:.(.*?),', init_s, re.S)[0],
        'userRole': re.findall('userRole:.(.*?),', init_s, re.S)[0],
        'userSchools': re.findall('userSchools:.\'(.*?)\',', init_s, re.S)[0],
        'userSchoolType': re.findall('userSchoolType:.\'(.*?)\',', init_s, re.S)[0],
        'schoolType': re.findall('schoolType:.\'(.*?)\',', init_s, re.S)[0],
        'promoteId': ''
    }

    headers['Cookie'] = get_cookies()
    response = requests.get(browser.current_url[:browser.current_url.rfind('/')] + '/' + 'Svc/UserInfo', headers=headers)

    data = json.loads(response.text)['data']

    for info in data:
        user_info[info] = data[info]

    return user_info


def get_class_list():
    browser.get('https://degree.qingshuxuetang.com/hngd/Student/CourseList')

    class_html = browser.page_source

    document = pq(class_html)
    print(document('.container .page-header small').text())
    class_items = document('.container.pt20 .row .panel-body').items()
    for item in class_items:
        class_name = item.find('.course_name').text()
        class_link = unescape(item.find('.button.btn-lg.btn-green').attr('href'))
        current_class_info = {
            'name': class_name,
            'url': 'https://degree.qingshuxuetang.com/hngd/Student/' + str(class_link),
            'courseId': re.findall('courseId=(.*?)&', class_link)[0],
            'teachPlanId': re.findall('teachPlanId=(.*?)&', class_link)[0],
            'periodId': re.findall('periodId=(\d+)', class_link)[0]
        }
        user_class_info[str(re.findall('courseId=(.*?)&', class_link)[0])] = current_class_info

    return user_class_info


def upload_study_record_begin():
    url = "https://degree.qingshuxuetang.com/hngd/Student/UploadStudyRecordBegin"

    querystring = {"_t": "1563719597001"}

    payload = "{\n    \"classId\": \"271\",\n    \"contentId\": \"kcjs_1\",\n    \"contentType\": 11,\n    \"courseId\": \"1298\",\n    \"periodId\": \"11\",\n    \"position\": 0,\n    \"schoolId\": \"9\"\n}"
    headers = {
        'Host': "degree.qingshuxuetang.com",
        'Connection': "keep-alive",
        'Content-Length': "117",
        'Pragma': "no-cache",
        'Cache-Control': "no-cache",
        'Accept': "application/json",
        'Origin': "https://degree.qingshuxuetang.com",
        'X-Requested-With': "XMLHttpRequest",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        'Content-Type': "application/json",
        'Referer': "https://degree.qingshuxuetang.com/hngd/Student/CourseShow?courseId=1298&teachPlanId=271&periodId=11&cw_nodeId=kcjs_1",
        'Accept-Encoding': "gzip, deflate, br",
        'Accept-Language': "zh-CN,zh;q=0.9,ja;q=0.8,ko;q=0.7,en;q=0.6",
        'cache-control': "no-cache"
    }

    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

    print(response.text)


def upload_study_record_continue():
    url = "https://degree.qingshuxuetang.com/hngd/Student/UploadStudyRecordContinue"

    querystring = {"_t": "1563601371233"}

    payload = "{\n    \"recordId\": *,\n    \"position\": 103\n}"
    headers = {
        'Host': "degree.qingshuxuetang.com",
        'Connection': "keep-alive",
        'Content-Length': "35",
        'Pragma': "no-cache",
        'Cache-Control': "no-cache",
        'Accept': "application/json",
        'Origin': "https://degree.qingshuxuetang.com",
        'X-Requested-With': "XMLHttpRequest",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        'Content-Type': "application/json",
        'Referer': "https://degree.qingshuxuetang.com/hngd/Student/CourseShow?teachPlanId=271&periodId=11&courseId=1298&cw_nodeId=kcjs_1",
        'Accept-Encoding': "gzip, deflate, br",
        'Accept-Language': "zh-CN,zh;q=0.9,ja;q=0.8,ko;q=0.7,en;q=0.6",
        'Cookie': "",
        'cache-control': "no-cache"
    }

    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

    print(response.text)


def main():
    login(conf.username, conf.password)
    get_class_list()
    init_cookies()
    init_user_info()

    for cookie in user_cookies:
        print(cookie, user_cookies[cookie])

    for item in user_info:
        print(item, user_info[item])

    for item in user_class_info:
        print(item, user_class_info[item])

    browser.quit()


if __name__ == '__main__':
    main()
