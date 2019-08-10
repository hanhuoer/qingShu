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
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--headless')
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.browser = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.browser, 10)

        self.document = {
            "cookies": {},
            "student": {},
            "semester": {},
            "task": {
                "semester": {},
                "class": {}
            }
        }

        self.headers = {
            'Host': "degree.qingshuxuetang.com",
            'Connection': "keep-alive",
            'Pragma': "no-cache",
            'Cache-Control': "no-cache",
            'Accept': "*/*",
            'Origin': "https://degree.qingshuxuetang.com",
            'X-Requested-With': "XMLHttpRequest",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
            'Content-Type': "application/json",
            'Accept-Encoding': "gzip, deflate, br",
            'Accept-Language': "zh-CN,zh;q=0.9,ja;q=0.8,ko;q=0.7,en;q=0.6",
            'cache-control': "no-cache"
        }

    def get_browser(self):
        return self.browser

    def quit(self):
        return self.browser.quit()

    """
    公用头部模板

    """

    def get_headers_template(self):
        return self.headers

    """
    @return document {student, cookies, task {semester, class}}
    """

    def get_document(self):
        return self.document

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
        为什么要登录? 因为要授权, 登录成功就是授权成功, 成功后我们应拿到 "通行证"
    """

    def login(self, username, password):
        self.browser.get('https://degree.qingshuxuetang.com/hngd/Home')

        self.document['account'] = {
            'username': username,
            'password': password
        }

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
            EC.presence_of_element_located((By.ID, 'loginByPwdBtn'))
        )
        login_button.click()

        error_text = pq(self.browser.page_source).find('#errorMsgPanel').text()

        if len(error_text) >= 1:
            self.browser.close()
            return '密码错误'
        else:
            # cookies
            login_time = time.time()
            while len(self.document['cookies']) < 4:
                if time.time() - login_time >= 10:
                    return '登录超时, 请重新登录'
                for cookie in self.browser.get_cookies():
                    self.document['cookies'].setdefault(cookie['name'], cookie['value'])
                if len(self.document['cookies']) < 4:
                    self.document['cookies'].clear()
                    time.sleep(1)

            return '登录成功'

    def spider_student_info(self):
        self.browser.get('https://degree.qingshuxuetang.com/hngd/Student/UserInfoBasic')
        student_info_html = self.browser.page_source

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

        identify_info = re.findall('window.KF5SupportBoxAPI.identify\((.*?)\);', student_info_html, re.S)[
            0]
        user_info['name'] = re.findall('"name".:."(.*?)",', identify_info, re.S)[0]
        user_info['number'] = re.findall('\'用户帐号.*value.*\'(.*?)\'},', identify_info, re.S)[0]

        info_pq = pq(student_info_html).find('#userEditForm')

        user_info['gender'] = re.findall('性别.*?class.*?>(.*?)</div>', info_pq.html(), re.S)[0]
        user_info['id_no'] = re.findall('身份证.*?class.*?>(.*?)</div>', info_pq.html(), re.S)[0]
        user_info['address'] = info_pq.find('input').attr('value')

        # info
        headers = self.get_headers_template()

        headers['Cookie'] = json_utils.json_parse_to_equivalent(self.document['cookies'])
        response = requests.get('https://degree.qingshuxuetang.com/hngd/Student/Svc/UserInfo', headers=headers)

        user_info_data = json.loads(response.text)['data']

        for info in user_info_data:
            user_info[info] = user_info_data[info]

        self.document['student'] = user_info

        return self.document['student']

    """
    @return current course
    """

    def spider_current_class(self):

        self.browser.get('https://degree.qingshuxuetang.com/hngd/Student/CourseList')
        document = pq(self.browser.page_source)

        self.document['task']['semester'] = {
            'current': re.findall('当前学期：(.*?)\s+开', document.text())[0],
            'begin': re.findall('开始时间：(.*?)\s+结', document.text())[0],
            'end': re.findall('结束时间：(.*?)\s+', document.text())[0]
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

            self.browser.get(current_class_info['url'])
            class_source = self.browser.page_source

            for a in pq(class_source).find('ul.tab li a'):
                k = ''
                v = ''
                for class_name in pq(a).attr('class').split(' '):
                    if class_name == 'active':
                        continue
                    k = class_name + '_url'
                v = 'https://degree.qingshuxuetang.com/hngd/Student/' + str(pq(a).attr('href'))
                current_class_info.setdefault(k, v)

            self.document['task']['class'].setdefault(str(re.findall('courseId=(.*?)&', class_link)[0]),
                                                      current_class_info)

        return self.document['task']

    """
    find all semester...
    """

    def find_all_semester(self):
        self.browser.get('https://degree.qingshuxuetang.com/hngd/Student/CourseList')
        document = pq(self.browser.page_source)

        self.document['semester'].setdefault('0', {
            'title': '当前学期',
            'html': document.find('#currentCourseDiv').html()
        })

        serial = 1
        for semester in document.items('#allCourseDiv .row'):
            key = semester.children('div:nth-child(1)').text()
            value = semester.html()
            self.document['semester'].setdefault(str(serial), {
                'title': key,
                'html': value
            })
            serial += 1
        return self.document['semester']

    """
    according to semester spider class info
    """

    def spider_choose_class(self, semester):
        choose_semester_info = self.document['semester'].get(semester)
        document = pq(choose_semester_info['html'])

        self.document['task']['semester'] = {
            'current': choose_semester_info['title'],
        }

        for item in document('.col-md-3.col-sm-4.col-xs-12').items():
            class_name = item.text()
            class_link = unescape(item.find('a').attr('href'))
            current_class_info = {
                'name': class_name,
                'url': 'https://degree.qingshuxuetang.com/hngd/Student/' + str(class_link),
                'courseId': re.findall('courseId=(.*?)&', class_link)[0],
                'teachPlanId': re.findall('teachPlanId=(.*?)&', class_link)[0],
                'periodId': re.findall('periodId=(\d+)', class_link)[0]
            }

            self.browser.get(current_class_info['url'])
            class_source = self.browser.page_source

            # class detail url, like home_work_url ... back_url
            for a in pq(class_source).find('ul.tab li a'):
                k = ''
                v = ''
                for class_name in pq(a).attr('class').split(' '):
                    if class_name == 'active':
                        continue
                    k = class_name + '_url'
                v = 'https://degree.qingshuxuetang.com/hngd/Student/' + str(pq(a).attr('href'))
                current_class_info.setdefault(k, v)

            self.document['task']['class'].setdefault(str(re.findall('courseId=(.*?)&', class_link)[0]),
                                                      current_class_info)

        return self.document['task']

    """
    作业
    """

    def spider_class_home_work(self):

        headers = self.get_headers_template()
        headers['Cookie'] = json_utils.json_parse_to_equivalent(self.document['cookies'])

        for k, v in self.document['task']['class'].items():

            self.document['task']['class'][k]['test'] = []

            response = requests.get(v['homework_url'], headers=headers)
            document = pq(response.text)

            for item in document.find('.exercise-body').items():
                url = re.findall('ExercisePaper(.*?)"', item.html(), re.S)[0]

                exercise_id = re.findall('exerciseId=(.*?)&', url, re.S)[0]

                basic_params = 'courseId=' + v['courseId'] + '&exerciseId=' + exercise_id + '&teachPlanId=' + v[
                    'teachPlanId'] + '&periodId=' + v['periodId']

                test_url = 'https://degree.qingshuxuetang.com/hngd/Student/ExercisePaper?' + basic_params
                re_test_url = 'https://degree.qingshuxuetang.com/hngd/Student/ExercisePaper?' + basic_params + '&isRetest=yes'
                answer_url = 'https://degree.qingshuxuetang.com/hngd/Student/ViewExerciseAnswer?' + basic_params
                save_url = 'https://degree.qingshuxuetang.com/hngd/Student/ExercisePaper?courseId=' + v[
                    'courseId'] + '&exerciseId=' + exercise_id + '&action=save'
                submit_url = 'https://degree.qingshuxuetang.com/hngd/Student/ExercisePaper?courseId=' + v[
                    'courseId'] + '&exerciseId=' + exercise_id + '&action=submit'

                student_id = ''

                test_html = requests.get(test_url, headers=headers).text
                test_document = pq(test_html)
                for input in test_document.find('#form1 input'):
                    if input.name == 'studentId':
                        student_id = input.value

                self.document['task']['class'][k]['test'].append({
                    'studentId': student_id,
                    'exerciseId': exercise_id,
                    'title': item.find('.title').text(),
                    'status': item.find('.exercise-status').text(),
                    'test_url': test_url,
                    're_test_url': re_test_url,
                    'answer_url': answer_url,
                    'save_url': save_url,
                    'submit_url': submit_url
                })

    """
    爬取作业答案
    """

    def spider_home_work_answer(self):
        headers = self.get_headers_template()
        headers['Cookie'] = json_utils.json_parse_to_equivalent(self.document['cookies'])
        headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'

        for k, v in self.document['task']['class'].items():
            if len(v['test']) == 0:
                continue
            else:
                for home_work in v['test']:

                    response = requests.post(home_work['answer_url'], headers=headers)
                    document = pq(response.text)

                    answer = {}

                    for item in document.items('.test'):
                        for input in item.find('.test-heading input'):
                            answer.setdefault(input.name, input.value)

                        content = item.find('.test-heading input')[0].name
                        answer_key = content[:-(content[::-1].find('.')) - 1] + '.answer'
                        answer_detail = re.findall('标准答案：(.*?)解', item.text(), re.S)[0].replace('\n', '')

                        # clear data
                        answer_type = -1
                        for i in list(answer_detail):
                            ascii_i = ord(i)
                            if (65 <= ascii_i <= 90) or (97 <= ascii_i <= 122):
                                # 这不是一道选择题
                                answer_type = 1
                                break
                            else:
                                # 这是一道选择题
                                answer_type = 2

                        if answer_type == 1:
                            answer_detail = list(answer_detail)
                        elif answer_detail == 2:
                            answer_detail = answer_detail

                        answer.setdefault(answer_key, answer_detail)

                    answer.setdefault('studentId', home_work['studentId'])
                    home_work['answer'] = answer

    """
    提交作业
    """

    def submit_home_work(self):
        headers = self.get_headers_template()
        headers['Cookie'] = json_utils.json_parse_to_equivalent(self.document['cookies'])
        headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'

        for k, v in self.document['task']['class'].items():
            if len(v['test']) == 0:
                continue
            else:
                for test in v['test']:
                    querystring = {"_t": int(time.time() * 1000)}
                    response = requests.post(test['submit_url'], headers=headers, data=test['answer'],
                                             params=querystring)
                    print('[system]' + 'submit home work; current major is: ' + v['name'] + ', and the home work is: ' +
                          test['title'] + ', and result: ' + response.text)

    """
    获取需要学习课程的所有视频
    """

    def spider_class_video(self):
        for item in self.document['task']['class']:
            print(
                '[system] scan current class detail and current class is: ' + self.document['task']['class'][item][
                    'name'])

            self.document['task']['class'][item]['video'] = []

            while self.document['task']['class'][item]['video'] is None or len(
                    self.document['task']['class'][item]['video']) == 0:

                self.browser.get(self.document['task']['class'][item]['url'])
                class_html = self.browser.page_source

                class_detail_params = re.findall('playCourseware\((.*?)\);"', class_html)

                self.document['task']['class'][item]['video'] = []

                for param in class_detail_params:
                    self.document['task']['class'][item]['video'].append({
                        'classId': self.document['task']['class'][item]['teachPlanId'],
                        'contentId': param.split(',')[0],
                        'contentType': 11,
                        'courseId': self.document['task']['class'][item]['courseId'],
                        'periodId': self.document['task']['class'][item]['periodId'],
                        'position': 0,
                        'schoolId': self.document['student']['schoolId']
                    })

                if len(self.document['task']['class'][item]['video']) > 1:
                    self.document['task']['class'][item]['enable'] = True
                else:
                    self.document['task']['class'][item]['enable'] = False

        return self.document['task']['class']

    """
    获取开始学习视频的代码
    """

    def begin_study_video_record(self):
        url = "https://degree.qingshuxuetang.com/hngd/Student/UploadStudyRecordBegin"

        querystring = {"_t": int(time.time() * 1000)}

        headers = self.get_headers_template()
        headers['Cookie'] = json_utils.json_parse_to_equivalent(self.document['cookies'])

        result = []

        for item in self.document['task']['class']:

            print('[system] get the detail video code... and current class: ' + self.document['task']['class'][item][
                'name'])

            for detail in self.document['task']['class'][item]['video']:
                payload = {
                    "classId": detail['classId'],
                    "contentId": detail['contentId'],
                    "contentType": 11,
                    "courseId": self.document['task']['class'][item]['courseId'],
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

    """
    根据 @begin_study_video_record 获取到的学习代码, 上传学习视频记录, 进行更新学习时间
    """

    def upload_study_video_record(self, study_max_time):
        url = "https://degree.qingshuxuetang.com/hngd/Student/UploadStudyRecordContinue"

        querystring = {"_t": int(time.time() * 1000)}

        class_count = 0
        finish_count = 0

        for k, v in self.document['task']['class'].items():
            if not v['enable']:
                continue
            else:
                class_count += len(v['video'])

        print('[system] begin study video...')

        while finish_count < class_count:
            for k, v in self.document['task']['class'].items():
                if not v['enable']:
                    continue
                else:
                    for detail in v['video']:
                        study_time = time.time() - detail['studyTime']
                        if study_time >= study_max_time:
                            finish_count += 1
                            print('[finish] major: ' + v['name'] + ', video: ' + str(
                                detail['studyId']) + ', study time: ' + str(study_time) + '\'s')
                        else:
                            payload = {
                                'recordId': detail['studyId'],
                                'position': '103'
                            }

                            headers = self.get_headers_template()
                            headers['Cookie'] = json_utils.json_parse_to_equivalent(self.document['cookies'])

                            response = requests.request("POST", url, data=json.dumps(payload), headers=headers,
                                                        params=querystring)

                            print('[studying] study time: ' + str(study_time) + '\'s' + ', major: ' + v[
                                'name'] + ', class: ' + str(detail['studyId']) + ', result: ' + response.text)
            if finish_count < class_count:
                print('[system] 本轮学习时间已经全部提交, 等待下一轮继续...')
                # 休息 60s
                time.sleep(60)
