#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Program of Court Reservation of University of Chinese Academy of Sciences (PCRA)
Copyright © 2022 Alonzo S. LAU . All rights reserved .

@author:    Alonzo S. LAU
@email:     liuchong21s@ict.ac.cn
@info:      mailer.py   2022-03-23

"""

import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def sendemail(user, pwd, smtp_server, receiver, result):
    username = "同学"
    if result:
        title = "场地预约成功通知"
        content = "同学，你好！<br>" \
                  "预约已完成，请登录中国科学院大学网上办事大厅" \
                  " https://ehall.ucas.ac.cn/v2/site/ucenter?showroute=myAppointment " \
                  "提交申请 <br>" \
                  "祝好"
    else:
        title = "场地预约失败通知"
        content = "同学，你好！<br>" \
                  "预约失败，请改天再次尝试 <br>" \
                  "祝好"
    receivers = [receiver]
    server = smtplib.SMTP_SSL(smtp_server, port=465)
    message = MIMEMultipart()
    message['From'] = Header('中国科学院大学运动场地预约程序', 'utf-8')
    message['To'] = Header(username, 'utf-8')
    subject = title
    message['Subject'] = Header(subject, 'utf-8')

    text = MIMEText(content, 'html', 'utf-8')
    message.attach(text)

    try:
        server.login(user, pwd)
        server.sendmail(user, receivers, message.as_string())
        server.close()
        return True
    except smtplib.SMTPRecipientsRefused as e:
        print('Recipient refused')
    except smtplib.SMTPAuthenticationError as e:
        print('Auth error')
    except smtplib.SMTPSenderRefused as e:
        print('Sender refused')
    except smtplib.SMTPException as e:
        print(repr(e))
        return False
