import peewee
from datetime import datetime

from database_manager import DatabaseManager
import local_settings

database_manager = DatabaseManager(
    database_name=local_settings.DATABASE['name'],
    user=local_settings.DATABASE['user'],
    password=local_settings.DATABASE['password'],
    host=local_settings.DATABASE['host'],
    port=local_settings.DATABASE['port'],
)


class SearchKey(peewee.Model):
    id = peewee.AutoField(primary_key=True)
    search_key = peewee.TextField(null=False, verbose_name='SearchKey')
    search_date = peewee.DateTimeField(default=datetime.now)

    class Meta:
        database = database_manager.db


class SearchResult(peewee.Model):
    id = peewee.AutoField(primary_key=True)
    search_id = peewee.ForeignKeyField(null=False,
                                       model=SearchKey, backref='searchresults', on_delete='CASCADE')
    authors = peewee.TextField(null=True, verbose_name='Authors')
    title = peewee.TextField(null=True, verbose_name='Title')
    description = peewee.TextField(null=True, verbose_name='Description')
    publish_date = peewee.TextField(null=True, verbose_name='PublishDate')
    pic_url = peewee.TextField(null=True, verbose_name='PicUrl')
    article_url = peewee.TextField(null=True, verbose_name='ArticleUrl')
    # user: for user searchs/ schedule: for scheduled search
    search_type = peewee.CharField(
        max_length=10, null=True, verbose_name='SearchType')

    class Meta:
        database = database_manager.db


class Category(peewee.Model):
    id = peewee.AutoField(primary_key=True)
    name = peewee.CharField(max_length=100, null=False, verbose_name='Name')
    description = peewee.TextField(null=True, verbose_name='Description')
    create_date = peewee.DateTimeField(default=datetime.now)

    class Meta:
        database = database_manager.db


# class ScheduleResult(peewee.Model):
    # authors = peewee.TextField(null=True, verbose_name='Authors')
    # title = peewee.TextField(null=True, verbose_name='Title')
    # description = peewee.TextField(null=True, verbose_name='Description')
    # date = peewee.TextField(null=True, verbose_name='Date')
    # pic_url = peewee.TextField(null=True, verbose_name='PicUrl')
    # category = peewee.ForeignKeyField(Category, on_delete='CASCADE')
    # article_url = peewee.TextField(null=True, verbose_name='ArticleUrl')

    # class Meta:
    #     database = database_manager.db


class Author(peewee.Model):
    id = peewee.AutoField(primary_key=True)
    name = peewee.CharField(max_length=100, null=False, verbose_name='Name')
    position = peewee.CharField(
        max_length=100, null=True, verbose_name='Position')
    twitter_url = peewee.TextField(null=True, verbose_name='TwitterUrl')
    linkedin_url = peewee.TextField(null=True, verbose_name='LinkedinUrl')
    crunch_url = peewee.TextField(null=True, verbose_name='CrunchUrl')
    create_date = peewee.DateTimeField(default=datetime.now)

    class Meta:
        database = database_manager.db


class Tag(peewee.Model):
    id = peewee.AutoField(primary_key=True)
    name = peewee.TextField(null=False, verbose_name='Name')
    created_date = peewee.DateTimeField(default=datetime.now)

    class Meta:
        database = database_manager.db


class Article(peewee.Model):
    id = peewee.AutoField(primary_key=True)
    title = peewee.TextField(null=False, verbose_name='Title')
    description = peewee.TextField(null=True, verbose_name='Description')
    publish_time = peewee.TextField(null=True, verbose_name='PublishTime')
    pic_url = peewee.TextField(null=True, verbose_name='PicUrl')
    reading_time = peewee.CharField(
        max_length=50, null=True, verbose_name='ReadingTime')
    category = peewee.ForeignKeyField(
        Category, backref='articles', on_delete='CASCADE')
    html = peewee.TextField(null=True, verbose_name='HTML')

    class Meta:
        database = database_manager.db


class SearchResultArticle(peewee.Model):
    article_id = peewee.ForeignKeyField(
        Article, backref='searchresults', on_delete='CASCADE')
    searchresult_id = peewee.ForeignKeyField(
        SearchResult, backref='articles', on_delete='CASCADE')

    class Meta:
        database = database_manager.db
        primary_key = peewee.CompositeKey('article_id', 'searchresult_id')


class ArticleTag(peewee.Model):
    article_id = peewee.ForeignKeyField(
        Article, backref='tags', on_delete='CASCADE')
    tag_id = peewee.ForeignKeyField(
        Tag, backref='articles', on_delete='CASCADE')

    class Meta:
        database = database_manager.db
        primary_key = peewee.CompositeKey('article_id', 'tag_id')


class ArticleAuthor(peewee.Model):
    article_id = peewee.ForeignKeyField(
        Article, backref='authors', on_delete='CASCADE')
    author_id = peewee.ForeignKeyField(
        Author, backref='articles', on_delete='CASCADE')

    class Meta:
        database = database_manager.db
        primary_key = peewee.CompositeKey('article_id', 'author_id')
