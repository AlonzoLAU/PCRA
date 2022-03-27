#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Program of Court Reservation of University of Chinese Academy of Sciences (PCRA)
Copyright © 2022 Alonzo S. LAU . All rights reserved.

@author:    Alonzo S. LAU
@email:     liuchong21s@ict.ac.cn
@info:      config.py   2022-03-23

"""


class Config:
    timeout = 5
    minIdle = 10
    maxIdle = 20
    waitForUser = 60
    # shift = 5  # 定时任务，程序将在设定时间的前后一个shift内执行轮询
