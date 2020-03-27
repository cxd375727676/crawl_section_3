# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 10:19:20 2020

@author: Administrator

命令行运行
"""

import asyncio


async def foo():
    print("foo start")
    await asyncio.sleep(3)
    print("foo end")
    return "foo"


async def bar():
    print("bar start")
    await asyncio.sleep(5)
    print("bar end")
    return "bar"


async def main(flag):
    if flag == 1: # 版本1
        res = await asyncio.gather(foo(), bar()) # res是列表
        print("任务全部执行完毕")
        print(res)        
    if flag == 2: # 版本2
        # 封装成任务加入事件循环，但不管啥时候结束
        task_f = asyncio.create_task(foo())
        task_b = asyncio.create_task(bar())
        res_f = await task_f
        res_b = await task_b
        print(res_f)
        print(res_b)
    if flag == 3: #版本3
        task_f = asyncio.create_task(foo())
        task_b = asyncio.create_task(bar())
        res = await asyncio.wait([task_f, task_b])  # res是元组
        print(res)
  
    
    
if __name__ == '__main__':
    #asyncio.run(main(1))
    #asyncio.run(main(2))
    asyncio.run(main(3))