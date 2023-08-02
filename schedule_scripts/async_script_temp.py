#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
协程池(非真正意义上的协程池)定时执行脚本模板

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
import signal
import time
import asyncio
import argparse
import schedule     # pip install schedule

from datetime import datetime, timedelta


def getConfigs():
    """
    get_configs 获取命令行参数
    """
    parser = argparse.ArgumentParser()
    # 检查时间间隔
    parser.add_argument("--interval", "-i", 
                        type=int, default=int(timedelta(seconds=1).total_seconds()), # 默认间隔时间
                        help="Run interval. Unit: second. Default: %(default)s")
    # 最大异步worker
    parser.add_argument("--max-workers", 
                        type=int, default=1,  # 默认线程池容量
                        help="Max number of concurrent executions. =0 no limit, Default: %(default)s")
    # TODO: other arguments
    arguments = parser.parse_args()
    print(f"DEBUG: Args{ str(arguments)[len('Namespace'):] }")
    return arguments


def run(arguments):

    is_shutdown = False  
    
    def exitHandler(sig, frame):
        """
        exitHandler 优雅退出处理函数
        """
        nonlocal is_shutdown
        is_shutdown = True
        print(f"WARN: Catch single:{sig}, shutdown pool and waited running workers now ...")
    
    async def start(*args, **kwargs):
        # TODO: 要执行的异步代码
        print(f"start: args:{args}  kwargs:{kwargs}")
        await asyncio.sleep(10)   # 模拟耗时操作
        print(f"end: args:{args}  kwargs:{kwargs}")
        
    async def mainCoroutine():
        """
        mainCoroutine 主协程函数，用于多个运行子协程
        """
        pool = asyncio.Semaphore(arguments.max_workers)  # 创建asyncio.Semaphore模拟pool, 必须写在async函数内
        
        async def runFunc(fn, args, kwargs):
            """
            runFunc  使用Semaphore运行异步函数

            :param function fn: 要执行的async函数
            :param tuple args: 函数参数
            :param dict kwargs: 函数参数
            """
            async with pool:  # 当asyncio.Semaphore.acquire() <= 0 也就是正在运行的协程数大于等于max_workers时会发生阻塞
                if not is_shutdown:  # 没有受到停止信号时执行函数。反之收到停止信号之后没有执行的函数不在执行直到队列结束，正在执行的函数继续执行，实现优雅退出
                    await fn(*args, **kwargs)
        
        params_list = range(1, 10)  # TODO 模拟获取到的参数
        tasks = [asyncio.ensure_future(
            runFunc(start ,args=(_id,), kwargs={})  # TODO 传入要执行的函数和参数
        ) for _id in params_list] 
        await asyncio.gather(*tasks)
                    
    def do():
        asyncio.run(mainCoroutine()) # 运行一轮主协程直到完成
        if is_shutdown:  # 接收到退出信号之后执行完这一轮后直接退出程序不执行下一轮。
            print(f"WARN: All running threads was done, exit now")
            exit(0)
            
    # 处理常用的退出信号
    signal.signal(signal.SIGTERM, exitHandler)  # SIGTERM   信号值:15   行为: supervisorctl stop  /  kill -15
    signal.signal(signal.SIGINT, exitHandler)   # SIGINT    信号值:2    行为: CTRL+C
            
    return do    


if __name__ == '__main__':
    arguments = getConfigs()
    runner = run(arguments)
    schedule.every(arguments.interval).seconds.do(runner)   # 定时任务设置参考https://schedule.readthedocs.io/en/stable/
    while True:
        schedule.run_pending()
        time.sleep(1)