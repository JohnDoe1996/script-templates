#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
多线程池/多进程池定时执行脚本模板

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

import queue
import signal
import time
import schedule  # pip install schedule
import argparse

from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed, wait


def getConfigs():
    """
    get_configs 获取命令行参数
    """
    parser = argparse.ArgumentParser()
    # 检查时间间隔
    parser.add_argument("--interval", "-i", 
                        type=int, default=int(timedelta(seconds=1).total_seconds()), # 默认间隔时间
                        help="Run interval. Unit: second. Default: %(default)s")
    # 异步运行方式 (线程池/进程池)
    parser.add_argument("--pool", '-p',
                        type=str, choices=['thread', 'process'], default="thread",  # 默认 线程/进程 运行
                        help="Run script by thread or Process. Default: %(default)s")
    # 最大异步worker
    parser.add_argument("--max-workers", 
                        type=int, default=1,  # 默认线程池容量
                        help="Max number of concurrent executions. =0 no limit, Default: %(default)s")
    # TODO: other arguments
    arguments = parser.parse_args()
    print(f"DEBUG: Args{ str(arguments)[len('Namespace'):] }")
    return arguments


def run(arguments):
    
    pool = (ThreadPoolExecutor if arguments.pool.lower().startswith("thread")
            else ProcessPoolExecutor)(max_workers=arguments.max_workers)
    
    def exitHandler(sig, frame):
        """
        exitHandler 优雅退出处理函数
        """
        print(f"WARN: Catch single:{sig}, shutdown pool and waited running workers now ...")
        if sys.version_info.minor >= 9: # python3.9 shutdown 才有 cancel_futures 参数
            pool.shutdown(wait=True, cancel_futures=True)  # 停止线程池，wait=True:等待正在运行的线程/进程结束，cancel_futures=True:取消正在等待的线程/进程
        else:
            while True:
                try:
                    work_item = pool._work_queue.get_nowait()
                except queue.Empty:
                    break
                if work_item is not None:
                    work_item.future.cancel()
            pool.shutdown(wait=True)    
        print(f"WARN: All running threads was done, exit now")
        exit(0)
    
    def start(*args, **kwargs):
        # TODO: 要执行的异步代码
        print(f"start: args:{args}  kwargs:{kwargs}")
        time.sleep(10)   # 模拟耗时操作
        print(f"end: args:{args}  kwargs:{kwargs}")
        
    def do():
        params_list = range(1, 10)  # TODO 模拟要传递的参数列表
        workers = [pool.submit(start, int(_id)) for _id in params_list]
        wait(workers)
            
    # 处理常用的退出信号
    signal.signal(signal.SIGTERM, exitHandler)  # SIGTERM   信号值:15   行为: supervisorctl stop  /  kill -15
    signal.signal(signal.SIGINT, exitHandler)   # SIGINT    信号值:2    行为: CTRL+C
            
    return do    


if __name__ == '__main__':
    arguments = getConfigs()
    runner = run(arguments)
    schedule.every(arguments.interval).seconds.do(runner) # 定时任务设置参考https://schedule.readthedocs.io/en/stable/
    while True:
        schedule.run_pending()
        time.sleep(1)