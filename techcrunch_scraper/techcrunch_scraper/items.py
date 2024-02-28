import scrapy


class SearchKeyItem(scrapy.Item):
    search_key = scrapy.Field()


class SearchResultItem(scrapy.Item):
    search_id = scrapy.Field()   
    title = scrapy.Field()
    authors = scrapy.Field()
    description = scrapy.Field()
    publish_date = scrapy.Field()
    pic_url = scrapy.Field()

    
