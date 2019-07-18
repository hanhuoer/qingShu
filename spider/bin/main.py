import spider.core.qingshu_core as qingshu
import spider.conf.user_conf as conf


def main():
    core = qingshu.Core()

    core.jsessionid()
    core.anonymous_device()
    core.login(conf.username, conf.password)

    print(core.get_jsessionid())
    print(core.get_anonymous_token())
    print(core.get_device_token())
    print(core.get_access_token())
    print(core.get_id())


if __name__ == '__main__':
    main()
