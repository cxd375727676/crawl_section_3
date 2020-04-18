# -*- coding: utf-8 -*-
"""
python 3.7： 异步接口分析 + aiohttp异步爬取 + aiofiles异步写入文件

1.分析网页异步数据请求接口格式：
  API = https://dynamic1.scrape.cuiqingcai.com/api/movie
  - 页面列表api： f'{API}/?limit={页面总数}&offset={偏移量: (page-1)*10}'
  - 页面详情api： f'{API}/{影片id}'

2.定义一个task：
  爬取页面列表api -> 完成对应页面所有详情的影片数据爬取与保存[sub_tasks]

3.定义一个sub_task:
  爬取详情api -> 保存该条影片数据

4.电影详情（一行记录）的字段：
  id:     网址上自带编号
  name：  电影名称
  alias： 别名
  cover:  封面网址
  categories：影片类型(多个)
  directors： 导演
  actors：演员（多个）
  score:  评分
  dramma：剧情
  regions:上映地区（多个）
  published_at：上映时间
  minute：影片时长 
"""

import logging
import asyncio
import aiohttp
import aiofiles


CONCURRENCY = 20     # 设置aiohttp异步爬虫最大并发量
API = "https://dynamic1.scrape.cuiqingcai.com/api/movie"
TOTAL_PAGE = 10


def log_config(log_fname, log_level):
    """ 日志设置：日志文件记录 + 控制台输出 """
    logger = logging.getLogger()  # root logger
    logger.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    if log_fname is not None:
        fh = logging.FileHandler(log_fname, mode='w')
        fh.setFormatter(formatter)
        logger.addHandler(fh)


async def fetch_data(session, api):
    async with session.get(api) as response:
        try:
            logging.info(f"爬取：{api}")
            assert response.status == 200
            return await response.json()
        except:
            logging.error(f"爬取失败：{api}")


def extract(data):
    """ 从详情数据提取关键信息， 形成一行记录 """
    def _get(dict_, key):
        value = dict_.get(key)
        if value is None:
            return ""
        elif isinstance(value, int) or isinstance(value, float):
            return str(value)
        else:
            return value
        
    id_ = _get(data, "id")
    name = _get(data, "name")
    alias = _get(data, "alias")
    cover = _get(data, "cover")
    categories = ';'.join(_get(data, "categories"))
    directors = _get(data, "directors")
    director_names = ';'.join([_get(each, "name") for each in directors])
    actors = _get(data, "actors")
    actor_names = ';'.join([_get(each, "name") for each in actors])
    score = _get(data, "score")
    dramma = _get(data, "dramma")
    regions = ';'.join(_get(data, "regions"))
    published_at = _get(data, "published_at")
    minute = _get(data, "minute")
    record = [id_, name, alias, cover, categories, director_names, 
              actor_names, score, dramma, regions, published_at, minute]
    record = ','.join(record)
    record += '\n'
    return record


async def sub_task(session, detail_api, wf):
    """ 从 detail_api 提取关键数据 异步写入文件wf """
    logging.info(f"保存数据：{detail_api}")
    try:
        data = await fetch_data(session, detail_api)
        record = extract(data)
        await wf.write(record)
    except:
        logging.error(f"保存数据失败：{detail_api}")
    

def collect_id(data):
    """ 从摘要信息收集该页面上所有id """
    ids = []
    results = data.get("results")
    for movie in results:
        ids.append(movie.get("id"))
    return ids

         
async def task(session, page, wf) :
    """ page_api -> 该页面上所有详情信息异步写入 """
    page_api = f"{API}/?limit={TOTAL_PAGE}&offset={(page - 1) * 10}"
    data = await fetch_data(session, page_api)
    ids = collect_id(data)
    sub_tasks = []
    for id_ in ids:
        detail_api = f"{API}/{id_}"
        sub_tasks.append(asyncio.create_task(sub_task(session, detail_api, wf)))
    await asyncio.gather(*sub_tasks)

    
async def main(n_page, wf_name, log_fname=None, log_level=logging.INFO):
    log_config(log_fname, log_level)
    if n_page > TOTAL_PAGE:
        n_page = TOTAL_PAGE
        logging.warning("超过最大页面，以最大页面数爬取")
    async with asyncio.Semaphore(CONCURRENCY):
        async with aiohttp.ClientSession() as session:
            async with aiofiles.open(wf_name, "w", encoding="utf-8") as wf:
                header = ['id', 'name', 'alias', 
                           'cover', 'categories', 'directors', 'actors', 
                           'score', 'dramma', 'regions', 'published_at', 'minute']
                header = ','.join(header) + '\n'
                wf.write(header)
                tasks = []
                for page in range(1, 1 + n_page):
                    tasks.append(asyncio.create_task(task(session, page, wf)))
                await asyncio.gather(*tasks)


if __name__ == '__main__':
    n_page = 10
    wf_name = 'movies.csv'
    log_fname = 'spider_5.log'
    asyncio.run(main(n_page, wf_name, log_fname))
