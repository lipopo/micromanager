from wtforms import form, fields
from flask_admin.contrib.pymongo import ModelView, filters


class UserForm(form.Form):
    """
    用户信息表
    """
    uid = fields.StringField("Id") # 用户唯一id
    name = fields.StringField("Name") # 用户名
    hpwd = fields.StringField("Hashed Password") # 密码散列
    is_admin = fields.BooleanField("Admin")

    ctime = fields.DateTimeField("Create Time") # 用户创建时间
    utime = fields.DateTimeField("Update Time") # 用户信息更新时间


class UserView(ModelView):
    column_list = ("name", "is_admin", "ctime", "utime")
    form = UserForm

