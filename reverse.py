#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Program of Court Reservation of University of Chinese Academy of Sciences (PCRA)
Copyright © 2022 Alonzo S. LAU . All rights reserved.

@author:    Alonzo S. LAU
@email:     liuchong21s@ict.ac.cn
@info:      reverse.py   2022-03-23

"""
import argparse
import datetime
import json
import logging
import os
import pickle
import random
import subprocess
import sys
import time
from urllib.parse import urlencode

import requests

from config import Config
from mailer import sendemail


# badminton

# basketball
# baketball_time = [465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 476, 475]
# baketball_court = [[1053, 1054, 1055, 1056, 1057, 1058, 1059, 1060, 1061, 1062, 1079, 1073],
#                    [1063, 1064, 1065, 1066, 1067, 1068, 1069, 1070, 1071, 1072, 1080, 1074]]


class Login:
    page = 'http://sep.ucas.ac.cn'
    url = page + '/slogin'
    system = page + '/portal/site/416/2095'
    pic = page + '/randomcode.jpg'


class EHall:
    base = 'http://ehall.ucas.ac.cn/'
    post_url = base + 'site/reservation/launch'
    identify = base + '/login?Identify='


class NetworkSucks(Exception):
    pass


class AuthInvalid(Exception):
    pass


class ReserveCourt(object):
    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
    }

    def __init__(self, user, password, captcha=False):
        super(ReserveCourt, self).__init__()
        self.identity = ''
        self.choice = []
        self.court_id = []
        self.logger = logging.getLogger('logger')
        self.s = requests.Session()
        self.s.headers = self.headers
        self.s.timeout = Config.timeout
        self.login(user, password, captcha)
        self.init_choice()

    def get(self, url, *args, **kwargs):
        r = self.s.get(url, *args, **kwargs)
        if r.status_code != requests.codes.ok:
            raise NetworkSucks
        return r

    def post(self, url, *args, **kwargs):
        r = self.s.post(url, *args, **kwargs)
        if r.status_code != requests.codes.ok:
            raise NetworkSucks
        return r

    def init_choice(self):
        f = ''
        k = ''
        m = 0
        with open('choice', 'r', encoding='utf8') as fh:
            tmp = fh.readline()

            if tmp == "0\n":
                f = 'court_id/basketball.json'
                k = '45'
                m = 2
                self.logger.info("预约篮球场地已就绪")
            elif tmp == "1\n":
                f = 'court_id/badminton.json'
                k = '40'
                m = 8
                self.logger.info("预约羽毛球场地已就绪")
            else:
                self.logger.error("请输入正确球类编号：0代表篮球 1代表羽毛球")
                sys.exit()

            tmp = fh.readlines()
            for t in tmp:
                l_tmp = []
                t = t.split()
                l_tmp.append(t[0])
                l_tmp.append(int(t[1]) - 10)
                l_tmp.append(int(t[2]) - 1)
                self.choice.append(l_tmp)

        with open(f, 'r', encoding='utf8') as fh:
            self.court_id = []
            j = json.load(fh)
            for t in self.choice:
                n = t[1] * m + t[2]
                l_tmp = [t[0], j[k][n]['time_id'], j[k][n]['sub_id']]
                self.court_id.append(l_tmp)
        self.logger.info("参数设定(日期,时间,场地):" + str(self.court_id))
        # print(self.court_id)
        # sys.exit()

    def login(self, user, password, captcha):
        if os.path.exists('cookie.pkl'):
            self.load()
            if self.auth():
                return
            else:
                self.logger.info('cookie 过期')
                os.unlink('cookie.pkl')
        self.get(Login.page)
        data = {
            'userName': user,
            'pwd': password,
            'sb': 'sb'
        }
        if captcha:
            with open('captcha.jpg', 'wb') as fh:
                fh.write(self.get(Login.pic).content)
            data['certCode'] = input('input captcha >>> ')
        self.post(Login.url, data=data)
        if 'sepuser' not in self.s.cookies.get_dict():
            self.logger.error('登陆失败')
            sys.exit()
        self.save()
        self.auth()

    def auth(self):
        r = self.get(Login.system)
        identity = r.text.split('<meta http-equiv="refresh" content="0;url=')
        if len(identity) < 2:
            self.logger.error('登陆失败')
            return False
        identity_url = identity[1].split('"')[0]
        self.identity = identity_url.split('Identity=')[1].split('&')[0]
        self.get(identity_url)
        self.logger.info("登陆成功")
        return True

    def save(self):
        self.logger.info('保存 cookie ···')
        with open('cookie.pkl', 'wb') as f:
            pickle.dump(self.s.cookies, f)

    def load(self):
        self.logger.info('加载 cookie ···')
        with open('cookie.pkl', 'rb') as f:
            cookies = pickle.load(f)
            self.s.cookies = cookies

    def reserve(self):
        url = EHall.post_url
        # book_headers = { "Connection": "keep-alive", "accept": "application/json, text/plain, */*",
        # "accept-language": "zh-CN,zh;q=0.9", "content-type": "application/x-www-form-urlencoded", "sec-ch-ua": "\"
        # Not A;Brand\";v=\"99\", \"Chromium\";v=\"99\", \"Google Chrome\";v=\"99\"", "sec-ch-ua-mobile": "?0",
        # "sec-ch-ua-platform": "\"macOS\"", "sec-fetch-dest": "empty", "sec-fetch-mode": "cors", "sec-fetch-site":
        # "same-origin", "x-requested-with": "XMLHttpRequest", "referrer":
        # "https://ehall.ucas.ac.cn/v2/reserve/m_reserveDetail?id=17", "referrerPolicy":
        # "strict-origin-when-cross-origin", "Origin": "https://ehall.ucas.ac.cn", "User-Agent": "Mozilla/5.0 (
        # Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83
        # Safari/537.36", 'Cookie':'PHPSESSID=g75nscjg6o72u08t9djlhfo901;
        # sepuser="bWlkPTk1MjhmYTU5LTcwYjgtNDAwOS05ZDAwLWUwZjI2MTRkYWZhZQ==  "; vjuid=474040;
        # vjvd=ee6b66fea3318899c5da341c3a36631e; vt=163737938' } tmp = [{"date": "2022-03-24", "period": 476,
        # "sub_resource_id": 1080}, {"date": "2022-03-24", "period": 475, "sub_resource_id": 1074}]
        tmp = []
        for c in self.court_id:
            tmp.append({"date": c[0], "period": c[1], "sub_resource_id": c[2]})
        tmp = json.dumps(tmp)
        data = {
            "resource_id": 17,
            # 'code': None,
            # 'remarks': None,
            # 'deduct_num': None,
            "data": tmp
        }
        redata = urlencode(data)
        command = "curl 'https://ehall.ucas.ac.cn/site/reservation/launch' " \
                  "-H 'Cookie: vjuid=" + self.s.cookies.get("vjuid") + "; " \
                                                                       "vjvd=" + self.s.cookies.get("vjvd") + ";' " \
                                                                                                              "--data-raw '" + redata + "'"
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        out_str = out.decode('utf-8')
        if args.detail:
            self.logger.info("POST响应 ——> " + out_str)
        with open('post.log', 'a') as fh:
            fh.write("POST响应 ——> " + out_str + "\n")
        return out_str[5]


def init_logger():
    format_str = '[%(asctime)s] [%(levelname)s] %(message)s'
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch_formatter = logging.Formatter(format_str)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(ch_formatter)
    logger.addHandler(ch)


def main():
    init_logger()
    with open('auth', 'r', encoding='utf8') as fh:
        user = fh.readline().strip()
        password = fh.readline().strip()
    if args.captcha:
        captcha = True
    else:
        captcha = False
    c = ReserveCourt(user, password, captcha)
    # i = 5
    # while i:
    #     c.reserve()
    #     i -= 1
    # sys.exit()
    result = False
    re_auth = False

    launch_time = datetime.datetime.now()
    c.logger.info("程序运行日期: " + str(launch_time.date()))

    end_time = None
    i = 0
    if args.time:

        set_time = datetime.datetime(launch_time.year, launch_time.month, launch_time.day, args.time[0], args.time[1],
                                     0)
        with open('post.log', 'a') as fh:
            fh.write("用户设定时间：" + str(set_time) + '\n')

        ''' 在一段时间内密集轮询 会被拉黑 改为仅在开放预约后 POST 一次 '''
        # start_time = set_time + datetime.timedelta(seconds=-Config.shift) #
        # end_time = set_time + datetime.timedelta(seconds=Config.shift)

        start_time = set_time
        c.logger.info("轮询启动时间设定：" + str(start_time))
        # c.logger.info("轮询结束时间设定：" + str(end_time))
        c.logger.info("请耐心等待 ···")
        while datetime.datetime.now() < start_time:
            time.sleep(1)

    c.logger.info("轮询正式启动")
    with open('post.log', 'a') as fh:
        fh.write("轮询启动于" + str(datetime.datetime.now()) + "\n")
    while True:
        try:
            if re_auth:
                c.auth()
                re_auth = False
            s = c.reserve()
            i = i + 1
            if s == '0':
                c.logger.info("预约成功 轮询结束")
                c.logger.info("总计轮询" + str(i) + "次")
                with open('post.log', 'a') as fh:
                    fh.write("预约成功 轮询结束" + "\n")
                result = True
                break
            # if args.time:
            #     if datetime.datetime.now() > end_time:
            #         c.logger.info("预约失败 轮询结束")
            #         c.logger.info("总计轮询" + str(i) + "次")
            #         with open('post.log', 'a') as fh:
            #             fh.write("预约失败 轮询结束" + "\n")
            #         break
            # else:
            # if i > 1:
            c.logger.info("预约失败 轮询结束")
            c.logger.info("总计轮询" + str(i) + "次")
            with open('post.log', 'a') as fh:
                fh.write("预约失败 轮询结束" + "\n")
            break

            # courseid = c.enroll()
            # if not courseid:
            #     break
            # c.courseid = courseid
            # time.sleep(random.randint(Config.minIdle, Config.maxIdle))
        except IndexError as e:
            c.logger.info("Court not found, maybe not start yet")
            time.sleep(random.randint(Config.minIdle, Config.maxIdle))
        except KeyboardInterrupt as e:
            c.logger.info('user aborted')
            break
        except (
                NetworkSucks,
                requests.exceptions.ConnectionError,
                requests.exceptions.ConnectTimeout
        ) as e:
            c.logger.debug('network error')
        except AuthInvalid as e:
            c.logger.error('wait for user operating')
            re_auth = True
            time.sleep(Config.waitForUser)
            # re_auth next loop
        except Exception as e:
            c.logger.error(repr(e))
    if args.mail and os.path.exists('mailConfig'):
        with open('mailConfig', 'rb') as fh:
            user = fh.readline().strip().decode('utf-8')
            pwd = fh.readline().strip().decode('utf-8')
            smtp_server = fh.readline().strip().decode('utf-8')
            receiver = fh.readline().strip().decode('utf-8')
            sendemail(user, pwd, smtp_server, receiver, result)
            with open('post.log', 'a') as pfh:
                pfh.write("邮件发送于：" + str(datetime.datetime.now()) + "\n")


if __name__ == '__main__':
    with open('post.log', 'w') as fh:
        fh.write("程序启动于：" + str(datetime.datetime.now()) + "\n")

    parser = argparse.ArgumentParser(description="中国科学院大学运动场地预约程序(PCRA)")
    parser.add_argument('-c', '--captcha', action='store_true',
                        help='非校园网络下须添加此选项 根据 captcha.jpg 手动输入验证码')
    parser.add_argument('-d', '--detail', action='store_true',
                        help='启用此选项将在控制台输出 post 响应日志 否则精简输出')
    parser.add_argument('-m', '--mail', action='store_true',
                        help='启用此选项并在 mailConfig 存在时根据用户配置进行邮件通知')
    parser.add_argument('-t', '--time', nargs='+', type=int,
                        help='启用定时任务 由当日时分两项组成 如12:30为 -t 12 30 程序将在当日设定时间发送 post 请求 ')

    args = parser.parse_args()
    with open('post.log', 'a') as fh:
        fh.write("程序参数：" + str(args) + "\n")

    main()
    with open('post.log', 'a') as fh:
        fh.write("程序结束于：" + str(datetime.datetime.now()) + "\n")
