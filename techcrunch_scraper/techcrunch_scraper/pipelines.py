# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pdb
import logging
logging.info('pipeline++++++++++++++++++++++++++++++++++++')
print('iiiiiiiiiiiiiiiiiiinnnnnnnnnnnnnnnnnnnnnnnnn')
# from itemadapter import ItemAdapter
# from database_manager import DatabaseManager
# import local_settings 
# from .items import SearchKeyItem, SearchResultItem
# from models import SearchKey, SearchResult

pdb.set_trace()

# database_manager = DatabaseManager(
#     database_name=local_settings.DATABASE['name'],
#     user=local_settings.DATABASE['user'],
#     password=local_settings.DATABASE['password'],
#     host=local_settings.DATABASE['host'],
#     port=local_settings.DATABASE['port'],
# )


class StorePipeline:
    # def __init__(self) -> None:
    #     pass
        
    # def open_spider(self, spider):
    #     pass

    def close_spider(self, spider):
        print('cccccccccccccclllllllllllllooooooooooooosssssssssssseeeeeeeeeeeee')
        # if database_manager.db:
        #     database_manager.db.close()

    def process_item(self, item, spider):
        print('++++++++++++++++++++++++++++')
        try:
            print('sfdf333333333333333333333333333333333333333')
            # if isinstance(item, SearchResultItem):
            #     SearchResult.create(
            #         search_id=item['search_id'],
            #         description=item['description'],
            #         title=item['title'],
            #         authors=item['authors'],
            #         publish_date=item['publish_date'],
            #         pic_url=item['pic_url']
            #     )
            # else:
            #     print('-------------------------------')
        except Exception as e:
            print('Error', e)

        return item
