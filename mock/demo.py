import re
from pyquery import PyQuery as pq
from xml.sax.saxutils import unescape
from selenium import webdriver
import time


home = 'https://degree.qingshuxuetang.com/hngd/Home'

class_list = 'https://degree.qingshuxuetang.com/hngd/Student/CourseList'

class_dic = {}

driver = webdriver.Firefox()
driver.get(home)

driver.find_element_by_id('uname').send_keys('15839427939')
driver.find_element_by_id('pwd').send_keys('1206751678')
driver.find_element_by_id('loginBtn').click()

# get class html
driver.get(class_list)
class_html = driver.page_source
document = pq(class_html)
print("当前学期: " + document('#currentCourseDiv > div:nth-child(1) > div:nth-child(1)').text())
class_items = document(
    'html body div.wrapper div.container div#currentCourseDiv.books-all div.row div.col-md-3.col-sm-4.col-xs-12').items()
for item in class_items:
    class_name = re.findall('<span>(.*?)</span>', item.html())[0]
    class_link = re.findall('href="(.*?)">', unescape(item.html()))[0]
    class_dic[str(class_name)] = 'https://degree.qingshuxuetang.com/hngd/Student/' + str(class_link)

for k in class_dic:
    print(k, class_dic[k])

# https://degree.qingshuxuetang.com/hngd/Student/CourseStudy?courseId=1316&amp;teachPlanId=271&amp;periodId=11

driver.quit()
