from celery import Celery, shared_task
from celery.schedules import crontab
import argparse
from datetime import datetime, timedelta
import time
import os
import sys
import shutil
import logging

from scrapy.crawler import CrawlerProcess
from techcrunch_scraper.spiders.tech_spider import TechSpiderSpider
from models import SearchKey, SearchResult, Category, Tag, Author, Article, ArticleAuthor, ArticleTag, SearchResultArticle
from database_manager import DatabaseManager
import local_settings
# from techcrunch_scraper.celery import crawl

database_manager = DatabaseManager(
    database_name=local_settings.DATABASE['name'],
    user=local_settings.DATABASE['user'],
    password=local_settings.DATABASE['password'],
    host=local_settings.DATABASE['host'],
    port=local_settings.DATABASE['port'],
)


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
app = Celery('tasks', broker='redis://localhost:6379',
             backend='redis://localhost:6379')
app.conf.beat_schedule = {
    'my-periodic-task': {
        'task': 'tasks.crawl',
        'schedule': crontab(minute='*'),
    },
}

# @app.task

@shared_task()
def crawl(key, format):
    print('in Crawl')
    logger.debug('in Crawl')
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
    logger.info('after Crawl')

    after_crawl(path)
    return path


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


def schedule_crawl():
    current_time = datetime.now()
    scheduled_time = current_time.replace(
        hour=1, minute=59, second=0, microsecond=0)
    if current_time.hour >= 20:
        scheduled_time += timedelta(days=1)
    print(f'Scheduled Crawling task for {scheduled_time}')
    result = crawl.apply_async(
        args=[args.key, args.format], eta=scheduled_time)
    while not result.ready():
        time.sleep(1)
        print("Waiting for task to complete...")
    print("Crawling task completed.")


def validate_arguments(args):
    # if not args.key:
    #     print("Error: Search key is missing.")
    #     sys.exit(1)
    if not os.path.exists('./output'):
        os.makedirs('./output')
    if not os.path.exists('./downloaded'):
        os.makedirs('./downloaded')


def run_spider(key, format, path):
    output_filename = f'{path}/output.{format}'
    process = CrawlerProcess(
        settings={
            'FEED_FORMAT': format,
            'FEED_URI': output_filename,
        }
    )
    process.crawl(TechSpiderSpider, search_key=key)
    process.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='main.py')
    parser.add_argument(
        '-s', '--key', help='Search key for TechCrunch Spider')
    parser.add_argument('-f', '--format', default='json', choices=['json', 'csv', 'xml'],
                        help='Output format for scraped data (default: json)')
    args = parser.parse_args()

    validate_arguments(args)

    try:
        database_manager.create_tables(
            models=[SearchKey, SearchResult, Category, Tag, Author, Article,
                    ArticleAuthor, ArticleTag, SearchResultArticle])
        # if args.key:
        path = before_crawl(args.key)
        run_spider(args.key, args.format, path)
        after_crawl(path)
        # print('1')
        # r= crawl.delay(args.key, args.format) # delay() adds the task to celery queue for execution
        # print(r)
        # print('2')
        # else:
        #     schedule_crawl()

    except OSError as e:
        print(f"Error: Failed to create output directory: {e}")
        sys.exit(1)
    except Exception as error:
        print('Error', error)
    finally:
        # closing database connection.
        if database_manager.db:
            database_manager.db.close()
            print('Database connection is closed')
