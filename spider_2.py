# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 13:46:28 2020

@author: Administrator

python3.7

注意用命令行执行脚本，IPython也是loop中的一个event

静态URL + 异步爬取 + 结果一次性存入pandas数据框

耗时11秒左右

"""
import logging
import pandas as pd
from lxml import etree
import asyncio
from urllib.parse import urljoin
import aiohttp
import re
import time



TOTAL_PAGE = 10
BASIC_URL = "https://static1.scrape.cuiqingcai.com/"


def get_page_urls(n_pages):
    """ 获取前n_pages页面的url """
    yield BASIC_URL
    for i in range(2, n_pages + 1):
        yield BASIC_URL + 'page/{}'.format(i)


async def fetch_html(url):
    """ 获取源代码 """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                assert response.status == 200, "状态码={}".format(response.status)
                return await response.text()
    except:
        logging.error("获取{}源代码失败".format(url))


def extract_detail_urls(html):
    """ 从页面url源代码获取详情url """
    elements = etree.HTML(html)
    return elements.xpath("//a[@class='name']/@href")


def get_detail_info(html):
    """ 根据详情页面html获取关键信息 
    -------------------------------------
    cover:封面超链接
    name：影片名称
    categories：影片类型
    published_at：上映时间
    drama:剧情简介
    score：评分
    """
    elements = etree.HTML(html)
    cover = elements.xpath("//img[@class='cover']/@src")[0]
    name = elements.xpath("//h2/text()")[0]
    categories = ';'.join(elements.xpath("//div[@class='categories']/button/span/text()"))
    published_at = elements.xpath("//div[contains(@class,'info')]/span/text()")[-1]
    search = re.search('\d{4}-\d{2}-\d{2}', published_at)
    published_at = search.group() if search else None    
    drama = elements.xpath("//h3/following-sibling::p[1]/text()")[0].strip()
    score = elements.xpath("//p[contains(@class,'score')]/text()")[0].strip()
    score = float(score) if score else None
    info = {
            'cover': cover,
            'name': name,
            'categories': categories,
            'published_at': published_at,
            'drama': drama,
            'score': score
            }
    return info
 

async def sub_task(detail_url):
    """ 从详情页面获得影片信息存入result """
    global result
    detail_url = urljoin(BASIC_URL, detail_url)
    logging.info("{}开始爬取详情页面".format(detail_url))
    html = await fetch_html(detail_url)
    logging.info("{}成功获取详情源代码".format(detail_url))
    info = get_detail_info(html)
    result.append(info)
    logging.info("{}详情存入字典".format(detail_url))
    
    
async def one_task(page_url):
    """ 单任务：
    page_url --> 解析内容，获取详情 -->多个详情链接异步爬取 --> 存入result
    """
    logging.info("{}开始爬取页面网页".format(page_url))
    html = await fetch_html(page_url)
    logging.info("{}成功获取页面网页源代码".format(page_url))
    detail_urls = extract_detail_urls(html)
    sub_tasks = [sub_task(detail_url) for detail_url in detail_urls]
    await asyncio.gather(*sub_tasks)
   

async def execute_tasks(n_pages):
    page_urls = get_page_urls(n_pages)
    tasks = [one_task(page_url) for page_url in page_urls]    
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, filename='spider_2.log',
                    format='%(asctime)s - %(levelname)s: %(message)s')
    n_pages = 7
    assert n_pages < TOTAL_PAGE
    save_path = "保存路径"
    start = time.time()
    result = []
    asyncio.run(execute_tasks(n_pages))
    result = pd.DataFrame(result)
    result.to_excel(save_path, index=False)
    end = time.time()
    logging.info("用时{:.2f}秒".format(end - start))
   
