from wtforms import form, fields
from flask_admin.contrib.pymongo import ModelView, filters


class ArticleForm(form.Form):
    name = fields.StringField('Name')
    content = fields.StringField('Content')


class ArticleView(ModelView):
    column_list = ('name', )
    form = ArticleForm

