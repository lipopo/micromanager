import os

import bcrypt
import pymongo
from flask import flash, Flask, render_template, request, redirect
from flask.views import MethodView
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib import rediscli
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.consts import ICON_TYPE_GLYPH
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user
from redis import Redis

from exceptions import LoginRequiredException
from views import UserView


cwd = os.getcwd()
login_manager = LoginManager()
app = Flask(__name__)
login_manager.init_app(app)

app.config["SECRET_KEY"] = b"\xf7\x14\xecM3\x8f\xc1?6\x8cj\xcf\xca\x94\xd4\xb6"
app.config["MAX_CONTENT_LENGTH"] = 30 * 1024 * 1024
app.config["title"] = "MicroManager"

conn = pymongo.MongoClient()
db = conn.test


"""
Login Block

主要构建用户以及陌生用户等。
"""

class User(UserMixin):
    """
    User 用户对象
    用于flask-login全局注册
    """

    def __init__(
        self,
        name=None,
        uid=None,
        hpwd=None,
        is_admin=None,
        ctime=None,
        utime=None,
        **kwargs
    ):
        self.name = name
        self.uid = uid
        self._is_admin = is_admin

    @property
    def is_authenicated(self):
        return self.uid is not None

    @property
    def is_active(self):
        return self.uid is not None

    @property
    def is_anonymous(self):
        return self.uid is None

    @property
    def is_admin(self):
        return self._is_admin

    def get_id(self):
        return self.uid or None

    @classmethod
    def get(cls, user_id):
        user = db.user.find_one({"uid": user_id})

        if user is None:
            return cls()
        else:
            return cls(**user)


@login_manager.user_loader
def load_user(user_id):
    """
    加载用户
    """
    return User.get(user_id)


class LoginView(MethodView):
    def get(self):
        if current_user.is_authenticated:
            return redirect("/admin")
        return render_template("login.html", title=app.config["title"])

    def post(self):
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = db.user.find_one({"name": username})

        if user is None:
            flash("用户名不可用", "danger")
            return redirect("/login")
        elif bcrypt.checkpw(
                password.encode("utf8"),
                user.get("hpwd", "").encode("utf8")
            ):
            _user = User(**user)
            login_user(_user)
            # 鉴权通过可以登陆用户
            return redirect("/admin")
        else:
            # 鉴权失败
            flash("密码错误", "danger")
            return redirect("/login")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    flash("登出成功", "info")
    return redirect("/login")

app.add_url_rule("/login/", view_func=LoginView.as_view("login"))


"""
Admin Block

管理系统模块

主要涵盖：
    - 数据库管理
    - 文件夹管理
    - Redis管理等
"""
admin = Admin(
     app,
     name="MicroManager",
     base_template="admin/ex_master.html",
     template_mode="bootstrap4",
     index_view=AdminIndexView(
         name="主页",
         menu_icon_type=ICON_TYPE_GLYPH,
         menu_icon_value="bi-house"
))

admin.add_view(FileAdmin(
    os.path.join(cwd, "files"),
    name="文件管理",
    menu_icon_type=ICON_TYPE_GLYPH,
    menu_icon_value="bi-files"
))

admin.add_view(
    UserView(
        db.user,
        "用户管理",
        menu_icon_type=ICON_TYPE_GLYPH,
        menu_icon_value="bi-people"
))

admin.add_view(rediscli.RedisCli(
    Redis(),
    "Redis管理"
))



# check login
@app.before_request
def login_required():
    endpoint = request.endpoint
    if endpoint != "login" and endpoint is not None:
        if current_user.is_anonymous:
            raise LoginRequiredException


@app.errorhandler(LoginRequiredException)
def handle_login_required_exception(e):
    flash("请先登陆系统", "danger")
    return redirect("/login")

