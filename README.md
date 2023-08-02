# 自用脚本模板

### python定时任务脚本（schedule 实现）

> DIR:  ./schedule_scripts/

大部分模板实现了优雅退出(即收到Ctrl+C 、 supervisorcli stop 时会等待正在执行任务执行完再退出)。使用例子参考 csdn:

| 文件 | 简介 | 备注 |
|:---:|:---:|:---:|
| threads_process_script_temp.py | **基于线程池/进程池的定时任务脚本模板** | 已实现优雅退出 |
| async_script_temp.py | **基于伪协程池的定时任务模板** | 已实现优雅退出 |
| system_listener_script_temp.py | **获取系统信息（CPU/内存/硬盘）信息并报警脚本** | 无需优雅退出 |