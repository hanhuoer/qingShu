import json
import re
import time
from xml.sax.saxutils import unescape

import requests
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from mock.util import json_utils


class MockSpider:

    def __init__(self):
        options = webdriver.ChromeOptions()
        # 不加载图片,加快访问速度
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.browser = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.browser, 10)

        self.user_class_info = {}
        self.user_info = {}

        self.headers = {
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

    def get_user_info(self):
        return self.user_class_info

    def get_user_class_info(self):
        return self.user_class_info

    def get_browser(self):
        return self.browser

    """
    公用头部模板
    
    """

    def get_headers_template(self):
        return self.headers

    def get_cookies(self, username, password):
        self.browser.get('https://degree.qingshuxuetang.com/hngd/Home')
        username_input = self.wait.until(
            EC.presence_of_element_located((By.ID, 'uname'))
        )
        username_input.clear()
        username_input.send_keys(username)

        password_input = self.wait.until(
            EC.presence_of_element_located((By.ID, 'pwd'))
        )
        password_input.clear()
        password_input.send_keys(password)

        login_button = self.wait.until(
            EC.presence_of_element_located((By.ID, 'loginBtn'))
        )
        login_button.click()

    """
    
    @param username: target user's username
    @param password: target user's password
    @return: 应该返回一些有用的东西, 比如 cookies, 登陆后
        为什么要登录? 因为要授权, 登录成功就是授权成功, 成功后我们理应拿到 "通行证"
    """

    def login(self, username, password):
        self.browser.get('https://degree.qingshuxuetang.com/hngd/Home')

        username_input = self.wait.until(
            EC.presence_of_element_located((By.ID, 'uname'))
        )
        username_input.clear()
        username_input.send_keys(username)

        password_input = self.wait.until(
            EC.presence_of_element_located((By.ID, 'pwd'))
        )
        password_input.clear()
        password_input.send_keys(password)

        login_button = self.wait.until(
            EC.presence_of_element_located((By.ID, 'loginBtn'))
        )
        login_button.click()

        cookies = {}
        user_info = {}

        # cookies
        while len(cookies) < 5:
            for cookie in self.browser.get_cookies():
                cookies.setdefault(cookie['name'], cookie['value'])
            if len(cookies) < 5:
                time.sleep(1)

        # user info
        user_info_script = re.findall('Behavior\.init\((.*?)\);', self.browser.page_source, re.S)[0]
        user_info = {
            'college': re.findall('college.*?\'(.*?)\',', user_info_script, re.S)[0],
            'schoolId': re.findall('schoolId:.(.*?),', user_info_script, re.S)[0],
            'userId': re.findall('userId:.(.*?),', user_info_script, re.S)[0],
            'userRole': re.findall('userRole:.(.*?),', user_info_script, re.S)[0],
            'userSchools': re.findall('userSchools:.\'(.*?)\',', user_info_script, re.S)[0],
            'userSchoolType': re.findall('userSchoolType:.\'(.*?)\',', user_info_script, re.S)[0],
            'schoolType': re.findall('schoolType:.\'(.*?)\',', user_info_script, re.S)[0],
            'promoteId': ''
        }

        identify_info = re.findall('window.KF5SupportBoxAPI.identify\((.*?)\);', self.browser.page_source, re.S)[
            0]
        user_info['name'] = re.findall('"name".:."(.*?)",', identify_info, re.S)[0]
        user_info['number'] = re.findall('\'用户帐号.*value.*\'(.*?)\'},', identify_info, re.S)[0]

        headers = self.get_headers_template()

        headers['Cookie'] = json_utils.json_parse_to_equivalent(cookies)
        response = requests.get('https://degree.qingshuxuetang.com/hngd/Student/Svc/UserInfo', headers=headers)

        user_info_data = json.loads(response.text)['data']

        for info in user_info_data:
            user_info[info] = user_info_data[info]

        self.user_info = {
            'cookies': cookies,
            'user_info': user_info
        }

        return self.user_info

    # def get_current_class_info_v1(self):
    #     user_class_info = {}
    #
    #     self.browser.get('https://degree.qingshuxuetang.com/hngd/Student/CourseList')
    #     document = pq(self.browser.page_source)
    #
    #     user_class_info['semester'] = document('.container .page-header small').text()
    #     user_class_info = {
    #         'semester': {
    #             'current': re.findall('当前学期：(.*?)\s+开', document.text())[0],
    #             'begin': re.findall('开始时间：(.*?)\s+结', document.text())[0],
    #             'end': re.findall('结束时间：(.*?)\s+', document.text())[0]
    #         },
    #         'class': {}
    #     }
    #
    #     for item in document('#currentCourseDiv .row .col-md-3.col-sm-4.col-xs-12').items():
    #         class_name = item.text()
    #         class_link = unescape(item.find('a').attr('href'))
    #         current_class_info = {
    #             'name': class_name,
    #             'url': 'https://degree.qingshuxuetang.com/hngd/Student/' + str(class_link),
    #             'courseId': re.findall('courseId=(.*?)&', class_link)[0],
    #             'teachPlanId': re.findall('teachPlanId=(.*?)&', class_link)[0],
    #             'periodId': re.findall('periodId=(\d+)', class_link)[0]
    #         }
    #         user_class_info['class'].setdefault(str(re.findall('courseId=(.*?)&', class_link)[0]), current_class_info)
    #
    #     for item in user_class_info['class']:
    #         self.browser.get(user_class_info['class'][item]['url'])
    #         user_class_info['class'][item]['class_detail'] = json.loads(
    #             re.findall('studyRecordList...(.*?);', self.browser.page_source, re.S)[0])
    #         if len(user_class_info['class'][item]['class_detail']) > 1:
    #             user_class_info['class'][item]['enable'] = True
    #         else:
    #             user_class_info['class'][item]['enable'] = False
    #
    #     return user_class_info

    """
    @return current course
    """

    def get_current_class_info_v2(self):

        self.browser.get('https://degree.qingshuxuetang.com/hngd/Student/CourseList')
        document = pq(self.browser.page_source)

        self.user_class_info['semester'] = document('.container .page-header small').text()
        self.user_class_info = {
            'semester': {
                'current': re.findall('当前学期：(.*?)\s+开', document.text())[0],
                'begin': re.findall('开始时间：(.*?)\s+结', document.text())[0],
                'end': re.findall('结束时间：(.*?)\s+', document.text())[0]
            },
            'class': {}
        }

        for item in document('#currentCourseDiv .row .col-md-3.col-sm-4.col-xs-12').items():
            class_name = item.text()
            class_link = unescape(item.find('a').attr('href'))
            current_class_info = {
                'name': class_name,
                'url': 'https://degree.qingshuxuetang.com/hngd/Student/' + str(class_link),
                'courseId': re.findall('courseId=(.*?)&', class_link)[0],
                'teachPlanId': re.findall('teachPlanId=(.*?)&', class_link)[0],
                'periodId': re.findall('periodId=(\d+)', class_link)[0]
            }
            self.user_class_info['class'].setdefault(str(re.findall('courseId=(.*?)&', class_link)[0]),
                                                     current_class_info)

        # class detail
        for item in self.user_class_info['class']:
            print('[system] scan current class detail and current class is: ' + self.user_class_info['class'][item]['name'])
            self.user_class_info['class'][item]['class_detail'] = []
            while self.user_class_info['class'][item]['class_detail'] is None or len(
                    self.user_class_info['class'][item]['class_detail']) == 0:
                self.browser.get(self.user_class_info['class'][item]['url'])
                class_detail_params = re.findall('playCourseware\((.*?)\);"', self.browser.page_source)

                self.user_class_info['class'][item]['class_detail'] = []

                for param in class_detail_params:
                    self.user_class_info['class'][item]['class_detail'].append({
                        'classId': self.user_class_info['class'][item]['teachPlanId'],
                        'contentId': param.split(',')[0],
                        'contentType': 11,
                        'courseId': self.user_class_info['class'][item]['courseId'],
                        'periodId': self.user_class_info['class'][item]['periodId'],
                        'position': 0,
                        'schoolId': self.user_info['user_info']['schoolId']
                    })

                if len(self.user_class_info['class'][item]['class_detail']) > 1:
                    self.user_class_info['class'][item]['enable'] = True
                else:
                    self.user_class_info['class'][item]['enable'] = False

        return self.user_class_info

    def get_study_record_begin(self):
        url = "https://degree.qingshuxuetang.com/hngd/Student/UploadStudyRecordBegin"

        querystring = {"_t": int(time.time() * 1000)}

        headers = self.get_headers_template()
        headers['Cookie'] = json_utils.json_parse_to_equivalent(self.user_info['cookies'])

        result = []

        for item in self.user_class_info['class']:
            print('[system] get the detail video code... and current class: ' + self.user_class_info['class'][item]['name'])
            for detail in self.user_class_info['class'][item]['class_detail']:
                payload = {
                    "classId": detail['classId'],
                    "contentId": detail['contentId'],
                    "contentType": 11,
                    "courseId": self.user_class_info['class'][item]['courseId'],
                    "periodId": detail['periodId'],
                    "position": 0,
                    "schoolId": detail['schoolId']
                }
                response = requests.request("POST", url, data=json.dumps(payload), headers=headers, params=querystring)

                if response.status_code == 200:
                    result.append(json.loads(response.content)['data'])
                    detail.setdefault('studyId', json.loads(response.content)['data'])
                    detail.setdefault('studyTime', time.time())
        return result

    def study_video(self, study_max_time):

        url = "https://degree.qingshuxuetang.com/hngd/Student/UploadStudyRecordContinue"

        querystring = {"_t": int(time.time() * 1000)}

        class_count = 0
        finish_count = 0

        for k, v in self.get_user_class_info()['class'].items():
            if v['enable'] == False:
                continue
            else:
                class_count += len(v['class_detail'])

        print('[system] begin study video...')
        while finish_count < class_count:
            for k, v in self.get_user_class_info()['class'].items():
                if v['enable'] == False:
                    continue
                else:
                    for detail in v['class_detail']:
                        study_time = time.time() - detail['studyTime']
                        if study_time >= study_max_time:
                            finish_count += 1
                            print('[finish] study time: ' + str(study_time) + '\'s' + ', major: ' + v['name'] + ', class: ' + str(detail['studyId']))
                        else:
                            payload = {
                                'recordId': detail['studyId'],
                                'position': '103'
                            }

                            headers = self.get_headers_template()
                            headers['Cookie'] = json_utils.json_parse_to_equivalent(self.user_info['cookies'])

                            response = requests.request("POST", url, data=json.dumps(payload), headers=headers,
                                                        params=querystring)

                            print('[studying] study time: ' + str(study_time) + '\'s' + ', major: ' + v['name'] + ', class: ' + str(detail['studyId']) + ', result: ' + response.text)
            if finish_count < class_count:
                print('[system] 本轮学习时间已经全部提交, 等待下一轮继续...')
                # 休息 60s
                time.sleep(60)

