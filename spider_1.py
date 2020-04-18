# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 13:46:28 2020

@author: Administrator

静态URL + 同步爬取 + 结果一次性写入pandas数据框

耗时31秒多
"""
import logging
import pandas as pd
from lxml import etree
from urllib.parse import urljoin
import requests
import re
import time



TOTAL_PAGE = 10
BASIC_URL = "https://static1.scrape.cuiqingcai.com/"


def get_page_urls(n_pages):
    """ 获取前n_pages页面的url """
    yield BASIC_URL
    for i in range(2, n_pages + 1):
        yield BASIC_URL + 'page/{}'.format(i)


def fetch_html(url):
    """ 获取源代码 """
    try:
        r = requests.get(url)
        assert r.status_code == 200, "状态码={}".format(r.status_code)
    except:
        logging.error("获取{}源代码失败".format(url))
    else:
        return r.text
        

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
 

def main(n_pages, save_path):
    start = time.time()
    result = []
    page_urls = get_page_urls(n_pages)
    for page_url in page_urls:
        html = fetch_html(page_url)
        detail_urls = extract_detail_urls(html)
        for detail_url in detail_urls:   # 抽取的是相对url
            detail_url = urljoin(BASIC_URL, detail_url)
            logging.info("get {}".format(detail_url))
            html = fetch_html(detail_url)
            info = get_detail_info(html)
            result.append(info)
    result = pd.DataFrame(result)
    result.to_excel(save_path, index=False)
    end = time.time()
    print("用时{:.2f}秒".format(end - start))



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')
    n_pages = 7
    assert n_pages < TOTAL_PAGE
    save_path = "保存路径"
    main(n_pages, save_path)
