from flask import Flask
from my_blog import db   #导入数据库对象


class User(db.Model):   #建立模型 用户
    __tablename__="users"   #数据库表名
    id = db.Column(db.Integer,primary_key=True)   #主键 自增
    name = db.Column(db.String(16),unique=True)   #用户名
    email = db.Column(db.String(120),index=True,unique=True)   #邮箱
    password = db.Column(db.String(128))   #密码


class  Article(db.Model):   #建立模型 文章
    __tablename__="articles"    #数据库表名
    id = db.Column(db.Integer,primary_key=True)    #主键 自增
    name = db.Column(db.String(64), unique=True)    #文章名
    content = db.Column(db.Text())   #内容
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))    #外键
    user = db.relationship('User', backref='articles')   #关联 用户
#通过关联可以通过文章直接查询作者的各项数据，不用通过调取作者主键进行二次查找


class  Comment(db.Model):   #建立模型 文章
    __tablename__="comments"    #数据库表名
    id = db.Column(db.Integer,primary_key=True)    #主键 自增
    content = db.Column(db.Text())   #内容
    article_id = db.Column(db.Integer, db.ForeignKey("articles.id"))    #外键
    article = db.relationship('Article', backref='comments')   #关联 文章
    com_author_id = db.Column(db.Integer, db.ForeignKey("users.id"))    #外键 发表评论的作者