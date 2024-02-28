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
    search_id = peewee.ForeignKeyField(null=False,
                                       model=SearchKey, backref='results', on_delete='CASCADE')
    authors = peewee.TextField(null=True, verbose_name='Authors')
    title = peewee.TextField(null=True, verbose_name='Title')
    description = peewee.TextField(null=True, verbose_name='Description')
    publish_date = peewee.TextField(null=True, verbose_name='PublishDate')
    pic_url = peewee.TextField(null=True, verbose_name='PicUrl')

    class Meta:
        database = database_manager.db


class Category(peewee.Model):
    id = peewee.AutoField(primary_key=True)
    name = peewee.CharField(max_length=100, null=False, verbose_name='Name')
    description = peewee.TextField(null=True, verbose_name='Description')
    create_date = peewee.DateTimeField(default=datetime.now)

    class Meta:
        database = database_manager.db


class ScheduleResult(peewee.Model):
    authors = peewee.TextField(null=True, verbose_name='Authors')
    title = peewee.TextField(null=True, verbose_name='Title')
    description = peewee.TextField(null=True, verbose_name='Description')
    date = peewee.TextField(null=True, verbose_name='Date')
    pic_url = peewee.TextField(null=True, verbose_name='PicUrl')
    category = peewee.ForeignKeyField(Category, on_delete='CASCADE')

    class Meta:
        database = database_manager.db


class Author(peewee.Model):
    id = peewee.AutoField(primary_key=True)
    name = peewee.CharField(max_length=100, null=False, verbose_name='Name')
    position = peewee.CharField(max_length=100, null=True, verbose_name='Position')
    twitter_url = peewee.TextField(null=True, verbose_name='TwitterUrl')
    linkedin_url = peewee.TextField(null=True, verbose_name='LinkedinUrl')
    crunch_url = peewee.TextField(null=True, verbose_name='CrunchUrl')
    create_date = peewee.DateTimeField(default=datetime.now)

    class Meta:
        database = database_manager.db


class Article(peewee.Model):
    id = peewee.AutoField(primary_key=True)
    title = peewee.TextField(null=False, verbose_name='Title')
    description = peewee.TextField(null=True, verbose_name='Description')
    Publish_date = peewee.TextField(null=True, verbose_name='PublishDate')
    pic_url = peewee.TextField(null=True, verbose_name='PicUrl')
    category = peewee.ForeignKeyField(Category, backref='articles', on_delete='CASCADE')
    tegs = peewee.TextField(null=True, verbose_name='Tags')
    html = peewee.TextField(null=True, verbose_name='HTML')

    class Meta:
        database = database_manager.db


class ArticleAuthor(peewee.Model):
    article_id = peewee.ForeignKeyField(Article, backref='authors', on_delete='CASCADE')
    author_id = peewee.ForeignKeyField(Author, backref='articles', on_delete='CASCADE')

    class Meta:
        database = database_manager.db
        primary_key = peewee.CompositeKey('article_id', 'author_id')
