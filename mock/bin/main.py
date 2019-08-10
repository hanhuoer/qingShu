import mock.conf.user_conf as uc
import mock.conf.db_conf as dc
import mock.core.spider_core as sc
import pymongo
import _thread

client = pymongo.MongoClient(dc.MONGO_URL)
db = client[dc.MONGO_DB]


def study_video(thread_name, spider):
    spider.study_video(300)


def save_to_mongodb(table, result):
    db[table].find_one()
    try:
        if db[table].insert(result):
            print('[SUCCESS]', result)
    except Exception:
        print('[ERROR]', result)


def main():
    spider = sc.MockSpider()
    login_response = spider.login(uc.username, uc.password)
    print(login_response)
    class_info = spider.get_current_class_info_v2()
    spider.get_study_record_begin()

    for info in class_info['class']:
        print(info, class_info['class'][info]['enable'], class_info['class'][info]['class_detail'])

    result = {
        'student_info': login_response,
        'class_info': spider.get_user_class_info()
    }

    print(result)

    save_to_mongodb(login_response['user_info']['number'], result)

    # _thread.start_new_thread(study_video, ('thread_study', spider))
    spider.study_video(300)

    spider.browser.quit()


if __name__ == '__main__':
    main()
