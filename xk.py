# -*- coding:utf-8 -*-

import getopt
import sys
import requests
import hashlib
import json
import time

# Initialize Session
s = requests.Session()
ua = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0"}
s.headers.update(ua)

# Debug proxy
proxies = {
    "http": "http://127.0.0.1:8080"
}


def main(argv):
    username = ""
    password = ""

    try:
        if not argv:
            raise StandardError

        opts, args = getopt.getopt(argv, "hu:p:", ["help", "username=", "password="])
    except (StandardError, getopt.GetoptError):
        print 'Error: xk.py -u <username> -p <password>'
        print '   or: xk.py --username=<username> --password=<password>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h" or opt == "--help":
            print 'Usage: xk.py -u <username> -p <password>'
            print '   or: xk.py --username=<username> --password=<password>'

            sys.exit()
        elif opt in ("-u", "--username"):
            username = arg
        elif opt in ("-p", "--password"):
            password = arg

    if not username:
        print "Username is needed."
        sys.exit(2)

    if not password:
        print "Password is needed."
        sys.exit(2)

    # Get cookies
    s.get("http://bkjwxk.sdu.edu.cn")

    # Set properties to login
    hs = hashlib.md5()
    hs.update(password)
    password = hs.hexdigest()
    data = "j_username=" + username + "&j_password=" + password
    headers = {
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Referer": "http://bkjwxk.sdu.edu.cn/f/login",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest"
    }
    r = s.post("http://bkjwxk.sdu.edu.cn/b/ajaxLogin", data=data, headers=headers)

    # Check if is successful
    if r.text != "\"success\"":
        print "Login error"
        print "Detailed message: "
        print r.text
        sys.exit()

    # Search course
    course_num = raw_input("Course Number: ")

    js = search(course_num)

    # Course Name
    index = 0
    for result in js["object"]["resultList"]:
        index += 1
        print "Index: " + str(index)
        print "Name: " + result["KCM"]
        print "Course Index: " + result["KXH"]
        print "Remaining: " + str(result["kyl"])

    i = input("Index to choose: ")

    i = i - 1
    if i != -1:
        while 1:

            data = js["object"]["resultList"][index]
            if data["kyl"] > 0:
                headers = {
                    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                    "Referer": "http://bkjwxk.sdu.edu.cn/f/common/main"
                }
                url = "http://bkjwxk.sdu.edu.cn/b/xk/xs/add/" + course_num + "/" + data["KXH"]

                r = s.get(url, headers=headers)
                js = json.loads(r.text)
                print js["result"] + ": " + js["msg"]
                if js["result"] == "success":
                    break

            time.sleep(5)

            # Refresh json data
            js = search(course_num)


def search(course_num):
    data = "type=kc&currentPage=1&kch=" + course_num + "&jsh=&skxq=&skjc=&kkxsh="
    headers = {
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Referer": "http://bkjwxk.sdu.edu.cn/f/common/main",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest"
    }
    r = s.post("http://bkjwxk.sdu.edu.cn/b/xk/xs/kcsearch", data=data, headers=headers)
    return json.loads(r.text)


if __name__ == "__main__":
    main(sys.argv[1:])
