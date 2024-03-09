from celery import Celery

import shutil
import os
import datetime
from scrapy.crawler import CrawlerProcess

from techcrunch_scraper.spiders.tech_spider import TechSpiderSpider


app = Celery('tasks', broker='redis://localhost:6379',
             backend='redis://localhost:6379')

@app.task
def crawl(key, format):
    print('in Crawl')
    path = before_crawl(key)
    output_filename = f'{path}/output.{format}'
    process = CrawlerProcess(
        settings={
            'FEED_FORMAT': format,
            'FEED_URI': output_filename,
        }
    )

    process.crawl(TechSpiderSpider, search_key=key)
    process.start()

    after_crawl(path)

def before_crawl(key):
    now = datetime.now()
    path = f'./output/{key}_{now.strftime("%Y%m%d-%H%M%S")}'
    os.makedirs(path)
    return path

    # key = ''
    # path = before_crawl(key)
    # run_spider(key, args.format, path)
    # after_crawl(path)
    # import multiprocessing as mp
    # pool = mp.Pool()
    # pool.apply_async(crawl,args[args.key, args.format],eta=scheduled_time)


def after_crawl(path):
    # Move downloaded resources
    source_dir = 'downloaded'
    target_dir = path
    file_names = os.listdir(source_dir)
    for file_name in file_names:
        shutil.move(os.path.join(source_dir, file_name), target_dir)

    # zip folder
    shutil.make_archive(path, 'zip', path)
    print(path)
