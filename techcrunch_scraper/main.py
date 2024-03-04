import celery
import argparse
from datetime import datetime, timedelta
import time
import os
import sys
import shutil

from scrapy.crawler import CrawlerProcess
from techcrunch_scraper.spiders.tech_spider import TechSpiderSpider
from models import SearchKey, SearchResult, Category, Tag, Author, Article, ArticleAuthor, ArticleTag, SearchResultArticle
from database_manager import DatabaseManager
import local_settings

app = celery('tasks', broker='redis://localhost:6379/0')

database_manager = DatabaseManager(
    database_name=local_settings.DATABASE['name'],
    user=local_settings.DATABASE['user'],
    password=local_settings.DATABASE['password'],
    host=local_settings.DATABASE['host'],
    port=local_settings.DATABASE['port'],
)


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


def validate_arguments(args):
    # if not args.key:
    #     print("Error: Search key is missing.")
    #     sys.exit(1)
    if not os.path.exists('./output'):
        os.makedirs('./output')
    if not os.path.exists('./downloaded'):
        os.makedirs('./downloaded')


def before_crawl(key):
    now = datetime.now()
    path = f'./output/{key}_{now.strftime("%Y%m%d-%H%M%S")}'
    os.makedirs(path)
    return path

@app.task
def crawl(key, format):
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


def schedule_crawl():
    current_time = datetime.now()
    scheduled_time = current_time.replace(hour=4, minute=1, second=0, microsecond=0)
    if current_time.hour >= 4:
        scheduled_time += timedelta(days=1)
    print(f'Scheduled Crawling task for {scheduled_time}')
    crawl.apply_async(args.key, args.format, eta = scheduled_time)
    # key = ''
    # path = before_crawl(key)
    # run_spider(key, args.format, path)
    # after_crawl(path)


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
        if args.key:
            # path = before_crawl(args.key)
            # run_spider(args.key, args.format, path)
            # after_crawl(path)
            crawl(args.key, args.format)
        else:
            schedule_crawl()

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
