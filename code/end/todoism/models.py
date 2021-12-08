# -*- coding: utf-8 -*-
"""
    :author: ZFF
    :email: <helloworldzff@163.com>
"""
import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from todoism.extensions import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, index=True, comment="用户名") #
    telnumber = db.Column(db.String(11), unique=True, comment="手机号") #
    password_hash = db.Column(db.String(128), comment="密码hash") #
    gender = db.Column(db.SmallInteger, comment="性别，男1 女2") #
    borth = db.Column(db.DateTime, comment="出生年月的时间戳") #
    address = db.Column(db.String(100), comment="住址") #
    type = db.Column(db.SmallInteger, comment="类型，管理员8 维修人员4 巡检人员2 设备负责人1") #
    status = db.Column(db.SmallInteger, comment="状态 正常1 删除9") #
    uptime = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="登录时间，每次更新") #
    locale = db.Column(db.String(20))
    items = db.relationship('Item', back_populates='author', cascade='all')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    done = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', back_populates='items')
