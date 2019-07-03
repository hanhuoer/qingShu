import requests
import time
import uuid


class Core:
    JSESSIONID = ''
    AnonymousToken = ''
    DeviceToken = ''
    AccessToken = ''
    Id = ''

    def __init__(self):
        self.anonymous_token = ''
        self.JSESSIONID = ''
        self.AnonymousToken = ''
        self.DeviceToken = ''
        self.AccessToken = ''
        self.Id = ''

    def get_jsessionid(self):
        return self.JSESSIONID

    def get_anonymous_token(self):
        return self.AnonymousToken

    def get_device_token(self):
        return self.DeviceToken

    def get_access_token(self):
        return self.AccessToken

    def get_id(self):
        return self.Id

    def jsessionid(self):
        get_jsessionid_url = 'https://degree.qingshuxuetang.com/hngd/Home'

        payload = ""

        headers = {
            'cache-control': "no-cache",
        }

        response = requests.request("GET", get_jsessionid_url, data=payload, headers=headers)

        self.JSESSIONID = response.cookies.get('JSESSIONID')

    def anonymous_device(self):
        get_anonymous_device_url = 'https://degree.qingshuxuetang.com/hngd/CreateAnonymous'

        cookies = "JSESSIONID=" + self.JSESSIONID

        querystring = {"_t": "1562080744102"}

        headers = {
            'Host': "degree.qingshuxuetang.com",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0",
            'Accept': "*/*",
            'Accept-Language': "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            'Accept-Encoding': "gzip, deflate, br",
            'Referer': "https://degree.qingshuxuetang.com/hngd/Home",
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
            'X-Requested-With': "XMLHttpRequest",
            'Content-Length': "0",
            'Connection': "keep-alive",
            'Cookie': cookies,
            'Pragma': "no-cache",
            'Cache-Control': "no-cache",
            'cache-control': "no-cache",
        }

        response = requests.request("POST", get_anonymous_device_url, headers=headers, params=querystring)

        self.AnonymousToken = response.cookies.get('AnonymousToken')
        self.DeviceToken = response.cookies.get('DeviceToken')

    def login(self, username, password):
        login_url = 'https://degree.qingshuxuetang.com/hngd/Login'

        idfa = str(uuid.uuid4())

        cookies = "device_token=" + self.DeviceToken + "; JSESSIONID=" + self.JSESSIONID + "; AnonymousToken=" + self.AnonymousToken

        querystring = {"_t": int(time.time() * 1000)}

        payload = "userNameTxt=" + username + "&passwordTxt=" + password + "&saveUserInfo=0&deviceInfoQS=%7B%22netType%22%3A1%2C%22appType%22%3A3%2C%22clientType%22%3A3%2C%22deviceName%22%3A%22PCWeb%22%2C%22osVersion%22%3A%22Win32%22%2C%22appVersion%22%3A%225.0%2B(Windows)%22%2C%22imei%22%3A%22%22%2C%22mac%22%3A%22%22%2C%22idfa%22%3A%" + idfa + "%22%7D&undefined="
        headers = {
            'Host': "degree.qingshuxuetang.com",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0",
            'Accept': "*/*",
            'Accept-Language': "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            'Accept-Encoding': "gzip, deflate, br",
            'Referer': "https://degree.qingshuxuetang.com/hngd/Home",
            'Content-Type': "application/x-www-form-urlencoded ; charset=UTF-8",
            'X-Requested-With': "XMLHttpRequest",
            'Content-Length': "348",
            'Connection': "keep-alive",
            'Cookie': cookies,
            'Pragma': "no-cache",
            'Cache-Control': "no-cache",
            'cache-control': "no-cache",
        }

        response = requests.request("POST", login_url, data=payload, headers=headers, params=querystring)

        self.AccessToken = response.cookies.get('AccessToken')
        self.Id = response.cookies.get('Id')
