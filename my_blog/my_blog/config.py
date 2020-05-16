from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker   #导入sessionmaker链接数据库

class Config(object):
    SQLALCHEMY_DATABASE_URI = "mysql://root:root@127.0.0.1:3306/blog_cn"   #登陆MySQL
    SQLALCHEMY_TRACK_MODIFICATIONS=True   #设置sqlalchemy自动跟踪数据库
    SQLALCHEMY_BINDS = {   #建立分支
        'blog_us': 'mysql://root:root@127.0.0.1:3306/blog_us'
    }
#来自CSDN博客  链接MySQL的方法


def dbFactory(blog_type):   #动态链接数据库
    my_engine = create_engine('mysql+pymysql://root:root@localhost/%s' % "blog_" + blog_type)
    #根据blog_type 动态建立数据库连接
    Session = sessionmaker(bind=my_engine)
    db_session = Session()  # 实例化session
    return db_session