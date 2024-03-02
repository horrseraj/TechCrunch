import scrapy


class SearchResultItem(scrapy.Item):
    search_id = scrapy.Field()   
    title = scrapy.Field()
    authors = scrapy.Field()
    description = scrapy.Field()
    publish_date = scrapy.Field()
    pic_url = scrapy.Field()
    article_url = scrapy.Field()
    search_type = scrapy.Field()

    
class ArticleItem(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    publish_time = scrapy.Field()
    pic_url = scrapy.Field()
    category = scrapy.Field()
    reading_time = scrapy.Field()
    html = scrapy.Field()
