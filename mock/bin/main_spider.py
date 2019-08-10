import mock.conf.user_conf as uc
import mock.conf.db_conf as dc
from mock.core.spider import MockSpider
import pymongo
import os
import _thread

client = pymongo.MongoClient(dc.MONGO_URL)
db = client[dc.MONGO_DB]


def clear():
    os.system('cls')


def study_video(thread_name, qingshu):
    qingshu.study_video(300)


def save_to_mongodb_v2(table, result):
    db[table].insert(result, check_keys=False)


def save_to_mongodb(table, result):
    try:
        if db[table].insert(result, check_keys=False):
            print('[SUCCESS]', result)
    except Exception:
        print('[ERROR]', result)


def welcome(name):
    print('*****************************************************************************')
    print('欢迎 ' + name + ' 使用刷客系统.')
    print('*****************************************************************************')


def v1():
    qing_shu = MockSpider()
    print(qing_shu.login(uc.username, uc.password))
    print(qing_shu.spider_student_info())
    print(qing_shu.spider_current_class())
    print(qing_shu.spider_class_home_work())
    print(qing_shu.spider_home_work_answer())
    print(qing_shu.submit_home_work())
    # print(qing_shu.spider_class_video())
    # print(qing_shu.begin_study_video_record())

    document = qing_shu.get_document()
    save_to_mongodb(document['student']['number'], document)

    # qing_shu.upload_study_video_record(400)

    qing_shu.quit()


"""
可选择
"""


def v2():
    is_continue = True
    while is_continue:
        qing_shu = MockSpider()

        # init data
        login_result = ''
        while not login_result == '登录成功':
            username = input('账号: ')
            password = input('密码: ')
            login_result = qing_shu.login(username, password)
            print(login_result)

        qing_shu.spider_student_info()
        semesters = qing_shu.find_all_semester().items()

        # welcome
        welcome(qing_shu.document['student']['name'])

        # choose semester
        print('-----------------------------------------------------------------------------')
        print('你有以下学期选择.')
        serial = []
        for k, v in semesters:
            print(k, v['title'])
            serial.append(k)
        print('-----------------------------------------------------------------------------')
        input_semester = ''
        while input_semester not in serial:
            input_semester = input('请选择你想要进入的学期: ')

        qing_shu.spider_choose_class(input_semester)

        print('你选择了 ' + qing_shu.document['semester'].get(str(input_semester))['title'])

        task = [1, 2]
        while len(task) > 0:

            for t in task:
                if t == 1:
                    print(t, '刷满课时')
                elif t == 2:
                    print(t, '刷满分作业')

            input_task = input('请选择要刷的任务: ')

            if input_task == '1':
                # class video
                print('[课时] 等待初始化课程视频...')
                qing_shu.spider_class_video()
                qing_shu.begin_study_video_record()
                qing_shu.upload_study_video_record(400)
                print(qing_shu.document['student']['name'] + ' 课时任务已经完成.')
                task.remove(int(input_task))
            elif input_task == '2':
                # home work
                print('[作业] 等待初始化作业...')
                qing_shu.spider_class_home_work()
                qing_shu.spider_home_work_answer()
                qing_shu.submit_home_work()
                print(qing_shu.document['student']['name'] + ' 作业已经全部提交.')
                task.remove(int(input_task))
            else:
                print('已退出')
                break

        # quit
        document = qing_shu.get_document()
        save_to_mongodb(document['student']['number'], document)
        qing_shu.quit()

        # re start?
        re_start = input('Do you want to start over? (yes or no): ')
        if re_start.lower() == 'yes':
            is_continue = True
        else:
            is_continue = False


def main():
    v2()


if __name__ == '__main__':
    main()
