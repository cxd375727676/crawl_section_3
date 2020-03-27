# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 14:08:14 2020

@author: 
    
思路：
编写异步函数extract_data: 从url获取数据data
然后针对一组urls，构造任务群，异步收集数据到列表
"""

import aiohttp
import asyncio
import logging
from urllib.parse import urljoin
import json
import os


TOTAL_PAGE = 10
BASIC_URL = "https://dynamic1.scrape.cuiqingcai.com" 
API_URL = urljoin(BASIC_URL, "api/movie")


def log_config():
    """ 日志设置：
    日志文件记录 + 控制台输出 """
    logger = logging.getLogger()  # root logger
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler('spider_4.log', mode='w')
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)

  
async def fetch_html(url):
    """ 获取源代码 """
    logging.info("开始爬{}".format(url))
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                assert response.status == 200, "状态码={}".format(response.status)
                logging.info("成功爬{}".format(url))
                return await response.text()
    except:
        logging.error("获取{}源代码失败".format(url))


async def extract_data(api):
    """ api接口 --> 解析json格式字符串为python对象"""
    html = await fetch_html(api)
    try:
        data = json.loads(html)
    except:
        logging.error("{}解析为python对象失败".format(api))
    else:
        logging.info("成功解析接口数据{}".format(api))
        return data


async def collect_data(apis):
    """ 异步获取各接口数据，汇总成data(列表)返回 """
    tasks = [extract_data(api) for api in apis]
    data = await asyncio.gather(*tasks)
    return data


def get_page_apis(n_page):
    """ 获取前n_page的网页api """
    for page in range(1, n_page + 1):
        page_api = "{}/?limit={}&offset={}".format(API_URL, TOTAL_PAGE, (page-1)*10)
        yield page_api


def get_detail_apis(ids):
    """ 获取指定id范围的详情api """
    for id_ in ids:
        detail_api = "{}/{}".format(API_URL, id_)
        yield detail_api


async def main(n_page):
    """ 获取全部摘要信息并保存为json文件,
    并提取部分页面的详情，各电影数据单独存为json文件"""
    log_config()
    total_pages = get_page_apis(TOTAL_PAGE)
    abstract = await collect_data(total_pages)   # 全部摘要信息  
    
    part_abstract = abstract[: n_page]
    ids = []
    for page_data in part_abstract:
        results = page_data.get("results")
        for result in results:
            ids.append(result.get("id"))
    detail_apis = get_detail_apis(ids)
    detail = await collect_data(detail_apis)  # 获取部分详细数据
    
    with open("abstract.json", "w") as wf:   # 全部摘要信息写入json文件
        json.dump(abstract, wf)
        logging.info("全部摘要信息写入")
    dir_ = ".\detail"
    if not os.path.exists(dir_): 
        os.makedirs(dir_)
    for item in detail:
        name = item.get('name')
        fpath = os.path.join(dir_, name + ".json")
        with open(fpath, "w") as f:
            json.dump(item, f)
            logging.info("{}详情成功写入".format(name))

if __name__ == '__main__':
    n_page = 3
    asyncio.run(main(n_page))
