# crawl_section_3
崔庆才-52讲轻松搞定网络爬虫（个人修改版）

【框架】<https://nbviewer.jupyter.org/github/cxd375727676/crawl_section_3/blob/master/introduction.ipynb>

- 静态网址：<https://static1.scrape.cuiqingcai.com/>
  - 原教程优化版采取 多进程+PyQuery解析+PyMongo储存数据
  - 由于爬虫是IO密集型任务，使用多线程可能较好
  - 线程过多时，可考虑协程（避免线程开启及切换，由程序员控制程序调度）
  - 实验表明，协程版spider_2.py约为11秒，同步版spider_1.py约耗时31秒，节约时间，又避免多线程的race condition及线程开销

- 动态网址：<https://dynamic1.scrape.cuiqingcai.com/>
  - [spider_3.ipynb](https://nbviewer.jupyter.org/github/cxd375727676/crawl_section_3/blob/master/spider_3.ipynb)



注：
1. mongodb基本操作见:<https://www.jianshu.com/p/195b8f1601d1?utm_campaign=maleskine&utm_content=note&utm_medium=seo_notes&utm_source=recommendation>及<https://www.cnblogs.com/songzhenhua/p/9312715.html>
2. Python也可异步读写Mongodb(motor+asyncio)，见<https://www.jianshu.com/p/2e8b79c819fb>
3. Python3.7异步特性参考<https://www.cnblogs.com/btxlc/p/10792477.html>
