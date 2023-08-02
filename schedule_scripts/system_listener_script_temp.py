#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
系统参数获取报警脚本

datetime: 2021.10.12
version: 1.0.0
author: John (zy1234500@outlook.com)
"""

import os, sys
# """
# 切换跟根目录  如果需的话   
# """
# # 获取当前脚本的目录路径
# current_dir = os.path.dirname(os.path.abspath(__file__))
# # 切换到上一级目录
# base_dir = os.path.dirname(current_dir)
# # 添加上一级目录为项目的根目录
# sys.path.append(base_dir)
# print(f"> base dir path is {base_dir}")
import time
import psutil
import argparse
import schedule    # pip install schedule

from datetime import datetime, timedelta



LAST_SEND_TS = 0  # 上一次报警时间 时间戳
SEND_SLEEP_TIME = timedelta(hours=1).total_seconds()  # 报警后多久才再测报警 单位秒


def getConfigs():
    """
    get_configs 获取命令行参数
    """
    parser = argparse.ArgumentParser()
    # 检查时间间隔
    parser.add_argument("--interval", "-i", 
                        default=int(timedelta(minutes=1).total_seconds()),
                        type=int,
                        help="Run interval. Unit: second. Default: %(default)s")
    # CPU占用临界百分比
    parser.add_argument("--cpu", "-c",
                        default=90,
                        type=float,
                        help="Critical percentage of CPU usage. Default: %(default)s. "
                             "If do not want to check this data set -1")
    # 内存占用临界百分比
    parser.add_argument("--memory", "-m",
                        default=95,
                        type=float,
                        help="Critical percentage of memory usage. Default: %(default)s. "
                             "If do not want to check this data set -1")
    # 硬盘占用临界百分比
    parser.add_argument("--disk", "-d",
                        default=90,
                        type=float,
                        help="Critical percentage of disk usage. Default: %(default)s. "
                             "If do not want to check this data set -1")
    arguments = parser.parse_args()
    print(f"DEBUG: Args{ str(arguments)[len('Namespace'):] }")
    return arguments


def checkSystemData(arguments):
    """
    check_system_data 检查系统参数

    :param obj args: get_configs() result
    """
    global LAST_SEND_TS
    txt, msg, warning = "", "", False
    if arguments.cpu >= 0:
        cpu = psutil.cpu_percent()   # type: float    # CPU占用
        txt += f"CPU:{cpu}%\t"
        if cpu >= arguments.cpu:
            msg += f"\nCPU占用超额定值{arguments.cpu}%"
            warning = True
    if arguments.memory >= 0:
        memory = psutil.virtual_memory().percent   # type: float    # 内存占用
        txt += f"内存:{memory}%\t"
        if memory >= arguments.memory:
            msg = f"\n内存占用超额定值{arguments.memory}%"
            warning = True
    if arguments.disk >= 0:
        disk = psutil.disk_usage(path="/").percent     # type: float   # 硬盘占用
        txt += f"硬盘:{disk}%\t"
        if disk >= arguments.disk:
            msg += f"\n硬盘占用超额定值{arguments.disk}%"
            warning = True
    print(txt)
    if warning:
        t = int(time.time())
        if not LAST_SEND_TS or t - LAST_SEND_TS > SEND_SLEEP_TIME:
            print(f"send: {txt}{msg}")  
            # TODO: 发送警报
            LAST_SEND_TS = t


if __name__ == '__main__':
    arguments = getConfigs()
    schedule.every(arguments.interval).seconds.do(checkSystemData, arguments) # 定时任务设置参考https://schedule.readthedocs.io/en/stable/
    while True:
        schedule.run_pending()
        time.sleep(1)