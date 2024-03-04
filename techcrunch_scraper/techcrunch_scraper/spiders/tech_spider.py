import scrapy
from typing import Any, Optional
from w3lib.html import remove_tags
from datetime import datetime, timedelta
import json

from models import SearchKey, SearchResult, Category, Tag, Author, Article, ArticleAuthor, ArticleTag, SearchResultArticle
from ..items import SearchResultItem, ArticleItem


class TechSpiderSpider(scrapy.Spider):
    name = "tech_spider"
    # allowed_domains = ["techcrunch.com"]
    # start_urls = ["https://techcrunch.com/"]

    def __init__(self, name: str | None = None, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.base_url = 'https://techcrunch.com/'
        self.search_url = 'https://search.techcrunch.com/search?p='
        self.result_per_page = 10
        self.pages_to_scrape = 1
        self.type = ''
        # self.search_key =''

    def start_requests(self):
        search_key = getattr(self, 'search_key', None)
        if search_key:
            self.type = 'user'
            search_id = self.store_searchkey(search_key)

            url = self.search_url + search_key
            yield scrapy.Request(url, callback=self.find_pages, cb_kwargs={'search_id': search_id})
        else:
            self.type = 'system'
            # Calculate yesterday
            one_day_ago = datetime.now() - timedelta(days=1)
            date = one_day_ago.strftime("%Y-%m-%d")

            key = 'AUTOMATIC SCHEDULE(System-Generated, every 24 hours at 04:01)'
            search_id = self.store_searchkey(key)
            # url = self.base_url + formatted_date
            
            url = f'{self.base_url}wp-json/wp/v2/posts?after={date}T00:00:00&before={date}T24:00:00&orderby=date&order=desc&page=1&_embed=true&_envelope=true'
            yield scrapy.Request(url, callback=self.parse_by_date, cb_kwargs={'search_id': search_id, 'date': date, 'i': 1})

    def parse_by_date(self, response, search_id, date, i):
        data = json.loads(response.body)
        if data['status'] != 400:            
            for j in range(len(data['body'])):
                item = SearchResultItem()
                item['search_id'] = search_id
                tmp = data['body'][j]['yoast_head_json']['og_title']
                tmp = tmp.replace("| TechCrunch",'')
                item['title'] = tmp # data['body'][j]['title']['rendered']
                tmp = str(data['body'][j]['excerpt']['rendered'])
                tmp = tmp.replace('<p>','')
                item['description'] = tmp[:200]
                item['article_url'] = data['body'][j]['yoast_head_json']['og_url'] 
                # Format the datetime as "Month Day, Year"
                tmp = data['body'][j]['yoast_head_json']['article_published_time'] 
                dt = datetime.strptime(tmp, "%Y-%m-%dT%H:%M:%S+00:00")
                formatted_date = dt.strftime("%B %d, %Y")
                item['publish_date'] = formatted_date
                item['pic_url'] = data['body'][j]['jetpack_featured_media_url']
                item['authors'] = data['body'][j]['yoast_head_json']['author']  
                item['search_type'] = self.type

                result_id = self.store_searchresult(item)

                yield item

                yield scrapy.Request(item['article_url'], self.parse_article, cb_kwargs={'result_id': result_id})

            i += 1
            url = f'{self.base_url}wp-json/wp/v2/posts?after={date}T00:00:00&before={date}T24:00:00&orderby=date&order=desc&page={i}&_embed=true&_envelope=true'
            yield scrapy.Request(url, callback=self.parse_by_date, cb_kwargs={'search_id': search_id, 'date': date, 'i': i})

    def find_pages(self, response, search_id):
        # Finding number of results
        results = response.css('div .compPagination span::text').get()
        try:
            num_results, *other = results.split(" ")
            # Finding number of result pages
            if num_results:
                num_results = int(num_results)
                pages = num_results // self.result_per_page + \
                    (num_results % self.result_per_page > 0)
                self.pages_to_scrape = pages

                for i in range(self.pages_to_scrape):
                    link = f'{response.url}&b={i*10 + 1}&pz=10'
                    yield scrapy.Request(link, callback=self.parse, cb_kwargs={'search_id': search_id})
        except:
            print('Error in find_pages')

    def parse(self, response, search_id):
        # Extracting search results
        lis = response.css('ol.mb-15 li.ov-a')
        try:
            for li in lis:
                item = SearchResultItem()
                item['search_id'] = search_id
                item['pic_url'] = li.css('a.thmb::attr(href)').get()
                authors = remove_tags(li.css('span.mr-15').get()).strip()
                item['authors'] = authors.removeprefix(
                    'By ').replace(' and', ',')
                item['publish_date'] = li.css('span.pl-15::text').get()
                item['title'] = remove_tags(li.css('h4 a').get())
                item['article_url'] = li.css('h4 a::attr(href)').get()
                item['description'] = remove_tags(li.css('p.fz-14').get())
                item['search_type'] = self.type

                result_id = self.store_searchresult(item)

                yield item

                yield scrapy.Request(item['article_url'], self.parse_article, cb_kwargs={'result_id': result_id})
        except:
            print('Error in parse')

    def parse_article(self, response, result_id):
        meta_data = {}
        meta_tags = response.css('meta')
        for tg in meta_tags:
            property_ = tg.attrib.get('property')
            name = tg.attrib.get('name')
            content = tg.attrib.get('content')
            if property_ or name:
                key = property_ if property_ else name
                meta_data[key] = content

        item = ArticleItem()
        # response.css('h1.article__title').get()
        item['title'] = meta_data['og:title']
        item['description'] = meta_data['sailthru.description']
        item['id'] = meta_data['cXenseParse:articleid']
        item['pic_url'] = meta_data['og:image']
        item['reading_time'] = meta_data['twitter:data2']
        item['publish_time'] = meta_data['article:published_time']
        # Extracting Category
        data = meta_data['mrf:tags']  # Primary Category
        elements = data.split(';')
        cat = None
        for segment in elements:
            if 'Primary Category:' in segment:
                cat = segment.split(':')[1].strip()
                break
        try:
            category = Category.get(Category.name == cat)
        except Category.DoesNotExist:
            category = Category.create(name=cat)
            # TODO: add Category fields by navigating to its page: replace & with - in url
        item['category'] = category.id

        yield item

        try:
            Article.get(Article.id == item['id'])
        except Article.DoesNotExist:
            self.store_article(item)

            # Extract tags and authors and store them
            tags = meta_data['sailthru.tags']
            for t in tags.split(','):
                try:
                    tag = Tag.get(Tag.name == t.strip())
                except Tag.DoesNotExist:
                    tag = Tag.create(name=t.strip())
                finally:
                    ArticleTag.create(article_id=item['id'], tag_id=tag.id)

            authors = meta_data['cXenseParse:author']  # comma seperated
            for auth in authors.split(','):
                try:
                    author = Author.get(Author.name == auth.strip())
                except Author.DoesNotExist:
                    author = Author.create(name=auth.strip())
                    # TODO: add Author fields by navigating to its page: links are in <div class="article__byline">
                finally:
                    ArticleAuthor.create(
                        article_id=item['id'], author_id=author.id)
        finally:
            SearchResultArticle.create(
                article_id=item['id'], searchresult_id=result_id)

    def store_searchkey(self, key):
        # Insert into SearchKey
        new_search = SearchKey.create(search_key=key)
        return new_search.id

    def store_searchresult(self, item):
        new_search_result = SearchResult.create(
            search_id=item['search_id'],
            authors=item['authors'],
            title=item['title'],
            description=item['description'],
            publish_date=item['publish_date'],
            pic_url=item['pic_url'],
            article_url=item['article_url'],
            search_type=item['search_type']
        )
        return new_search_result.id

    def store_article(self, item):
        Article.create(
            id=item['id'],
            title=item['title'],
            description=item['description'],
            publish_time=item['publish_time'],
            pic_url=item['pic_url'],
            category=item['category'],
            reading_time=item['reading_time']
        )

    # def is_desired_page(self, response, url):
    #     if response.url == url:
    #         return True
    #     else:
    #         return False
