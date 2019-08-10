# import requests
#
# class_id = [
#     '2008144',
#     '2008145',
#     '2008146',
#     '2008148',
#     '2008149'
# ]
# url = "https://degree.qingshuxuetang.com/hngd/Student/UploadStudyRecordContinue"
#
# querystring = {"_t": "1563601371233"}
#
# # payload = {
# #     'recordId': '2008145',
# #     'position': '103'
# # }
#
# payload = "{\n    \"recordId\": 2008145,\n    \"position\": 103\n}"
#
# headers = {
#     'Host': "degree.qingshuxuetang.com",
#     'Connection': "keep-alive",
#     'Content-Length': "35",
#     'Pragma': "no-cache",
#     'Cache-Control': "no-cache",
#     'Accept': "application/json",
#     'Origin': "https://degree.qingshuxuetang.com",
#     'X-Requested-With': "XMLHttpRequest",
#     'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
#     'Content-Type': "application/json",
#     'Referer': "https://degree.qingshuxuetang.com/hngd/Student/CourseShow?teachPlanId=271&periodId=11&courseId=1298&cw_nodeId=kcjs_1",
#     'Accept-Encoding': "gzip, deflate, br",
#     'Accept-Language': "zh-CN,zh;q=0.9,ja;q=0.8,ko;q=0.7,en;q=0.6",
#     'Cookie': "",
#     'cache-control': "no-cache"
# }
#
# for item in class_id:
#     payload = "{\n    \"recordId\": " + item + ",\n    \"position\": 103\n}"
#     response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
#     print(item, response.text)


import time
import json
import requests

class_id = [
    '2008144',
    '2008145',
    '2008146',
    '2008148',
    '2008149'
]

url = "https://degree.qingshuxuetang.com/hngd/Student/UploadStudyRecordContinue"

querystring = {"_t": int(time.time() * 1000)}

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

for item in class_id:
    payload = {
        'recordId': item,
        'position': '103'
    }
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers, params=querystring)
    print(item, response.text)




