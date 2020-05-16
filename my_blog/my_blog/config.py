from flask import Flask
from flask_sqlalchemy import SQLAlchemy   #导入SQLAlchemy模块


class Config(object):
    SQLALCHEMY_DATABASE_URI = "mysql://root:root@127.0.0.1:3306/blog_cn"   #登陆MySQL
    SQLALCHEMY_TRACK_MODIFICATIONS=True   #设置sqlalchemy自动跟踪数据库
    SQLALCHEMY_BINDS = {   #建立分支
        'blog_us': 'mysql://root:root@127.0.0.1:3306/blog_us'
    }
#来自CSDN博客  链接MySQL的方法