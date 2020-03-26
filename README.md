# crawl_section_3
崔庆才-52讲轻松搞定网络爬虫（个人修改版）

- 静态网址：<https://static1.scrape.cuiqingcai.com/>
  - 原教程优化版采取 多进程+PyQuery解析+PyMongo储存数据
  - 由于爬虫是IO密集型任务，使用多线程可能较好
  - 线程过多时，可考虑协程（避免线程开启及切换，由程序员控制程序调度）
  - 实验表明，协程版spider_2.py约为23秒，同步版spider_1.py约耗时31秒，节约时间，又避免多线程的race condition及线程开销

- 动态网址：<https://dynamic1.scrape.cuiqingcai.com/>
