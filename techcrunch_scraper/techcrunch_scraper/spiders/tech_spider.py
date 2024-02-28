import scrapy
from typing import Any, Optional
from w3lib.html import remove_tags

from models import SearchKey, SearchResult, ScheduleResult, Author, Article, ArticleAuthor
from ..items import SearchKeyItem, SearchResultItem


class TechSpiderSpider(scrapy.Spider):
    name = "tech_spider"
    allowed_domains = ["techcrunch.com"]
    start_urls = ["https://techcrunch.com/"]

    def __init__(self, name: str | None = None, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.base_url = 'https://techcrunch.com/'
        self.search_url = 'https://search.techcrunch.com/search?p='
        self.result_per_page = 10
        self.pages_to_scrape = 1
        # self.search_key =''

    def start_requests(self):
        search_key = getattr(self, 'search_key', None)
        if search_key:
            # Inser into SearchKey
            new_search = SearchKey.create(search_key=search_key)
            search_id = new_search.id

            url = self.search_url + search_key
            yield scrapy.Request(url, callback=self.find_pages, cb_kwargs={'search_id': search_id})

    def find_pages(self, response, search_id):
        # Finding number of results
        results = response.css('div .compPagination span::text').get()
        num_results, *other = results.split(" ")
        # Finding number of result pages
        if num_results:
            num_results = int(num_results)
            pages = num_results // self.result_per_page + \
                (num_results % self.result_per_page > 0)
            self.pages_to_scrape = pages

            for i in range(self.pages_to_scrape):
                url = f'{response.url}&b={i*10 +1}&pz=10'                
                yield scrapy.Request(url, callback=self.parse, cb_kwargs={'search_id': search_id})

    def parse(self, response, search_id):
        # Extracting search results
        lis = response.css('ol.mb-15 li.ov-a')
        for li in lis:
            item = SearchResultItem()
            item['search_id'] = search_id
            item['pic_url'] = li.css('a.thmb::attr(href)').get()
            authors = li.css('span.mr-15::text').get().strip()
            item['authors'] = authors.removeprefix('By ').replace(' and', ',')
            item['publish_date'] = li.css('span.pl-15::text').get()
            item['title'] = li.css('h4 a::text').get()
            item['description'] = li.css('p.fz-14::text').get()
            yield item
            
            

            


        
