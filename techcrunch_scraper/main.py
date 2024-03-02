from scrapy.crawler import CrawlerProcess
import argparse
from datetime import datetime
import os
import sys
import shutil
import logging

from techcrunch_scraper.spiders.tech_spider import TechSpiderSpider
from models import SearchKey, SearchResult, Category, Tag, Author, Article, ArticleAuthor, ArticleTag, SearchResultArticle
from database_manager import DatabaseManager
import local_settings


database_manager = DatabaseManager(
    database_name=local_settings.DATABASE['name'],
    user=local_settings.DATABASE['user'],
    password=local_settings.DATABASE['password'],
    host=local_settings.DATABASE['host'],
    port=local_settings.DATABASE['port'],
)
logging.getLogger('scrapy').setLevel(logging.DEBUG)


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
    if not args.key:
        print("Error: Search key is missing.")
        sys.exit(1)
    if not os.path.exists('./output'):
        os.makedirs('./output')
    if not os.path.exists('./downloaded'):
        os.makedirs('./downloaded')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='main.py')
    parser.add_argument(
        '-s', '--key', help='Search key for Genlib Spider', required=True)
    parser.add_argument('-f', '--format', default='json', choices=['json', 'csv', 'xml'],
                        help='Output format for scraped data (default: json)')
    args = parser.parse_args()

    validate_arguments(args)

    now = datetime.now()
    path = f'./output/{args.key}_{now.strftime("%Y%m%d-%H%M%S")}'

    try:
        os.makedirs(path)

        database_manager.create_tables(
            models=[SearchKey, SearchResult, Category, Tag, Author, Article, ArticleAuthor, ArticleTag, SearchResultArticle])

        run_spider(args.key, args.format, path)

        # Move downloaded resources
        source_dir = 'downloaded'
        target_dir = path
        file_names = os.listdir(source_dir)
        for file_name in file_names:
            shutil.move(os.path.join(source_dir, file_name), target_dir)

        # zip folder
        shutil.make_archive(path, 'zip', path)
        print(path)
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
