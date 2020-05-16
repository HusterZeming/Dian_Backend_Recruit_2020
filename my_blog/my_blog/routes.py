from flask import Flask
from my_blog.forms import *
from my_blog import app
from flask import g   #全局变量g存储用户信息

@app.before_request   #在处理request之前进行用户身份验证
def jwt_query_params_auth():
    if request.path == '/admin/doLogin':   #注册和登陆时跳过验证
        return
    if request.path == '/admin/doReg':
        return
    token = request.headers.get('authorization')   #通过请求头写入token
    result = parse_payload(token)   #解析token来校验传入的token parse_payload由blog_auth传入
    if not result['status']:
        return jsonify(result)
    g.db = dbFactory(result["data"]["area"])  #根据token解析出的area动态建立数据库链接  dbFactory由my_blog.config传入
    g.info = result['data']   #全局变量g存储用户信息


@app.route("/send",methods=['POST'])   #发表文章
def send():
    name = request.args.get('name')   #存储http请求中的输入
    content = request.args.get('content')
    user_id = g.info['id']   #通过全局变量g保存用户的id信息
    db_session = g.db   #通过全局变量g导入建立的db_session
    new_article = Article(name=name, content=content, user_id=user_id)
    new_article.user = db_session.query(User).filter(User.id == user_id).first()   #关联到作者
    db_session.add(new_article)   #加入数据库
    db_session.commit()   #提交到数据库
    return{   #返回json文件
         "article_name": new_article.name,
         "article_content": new_article.content,
         "author": new_article.user.name
    }


@app.route("/change",methods=['GET','POST'])   #修改文章
def change():
    name = request.args.get('name')   #存储http请求中的输入
    content = request.args.get('content')
    db_session = g.db   #通过全局变量g导入建立的db_session
    article = db_session.query(Article).filter(Article.name == name).first()   #查询该文章
    if article is None:  # 查询不到显示无效名字
        return jsonify("Invalid name!")
    user_id = g.info['id']   #判别是否是作者 只有作者可以改动
    if user_id == article.user_id:
        article.content = content
        db_session.add(article)
        db_session.commit()   #提交到数据库
        return{
            "article_name": article.name,
            "article_content": article.content,
            "author": article.user.name,
            }
    else:
        return jsonify("You can't change other people's articles!")


@app.route("/delete",methods= ['GET','POST'])   #删除文章
def delete():
    name = request.args.get('name')
    db_session = g.db
    article = db_session.query(Article).filter(Article.name == name).first()   #查询该文章
    if article is None:  # 查询不到显示无效名字
        return jsonify("Invalid name!")
    user_id = g.info['id']
    if user_id == article.user_id:  # 只有文章作者可以删除文章和评论
        comments = db_session.query(Comment).filter(Comment.article_id == article.id).all()  #查询该文章的评论
        if comments is None:
            pass
        else:
            for comment in comments:   #删除评论
                db_session.delete(comment)  # 从数据库中删除
                db_session.commit()  # 提交到数据库

        db_session.delete(article)   #从数据库中将文章删除
        db_session.commit()   #提交到数据库
        return jsonify("The "+article.name+" has been deleted")
    else:
        return jsonify("You can't delete other people's articles!")  #非作者不可删除


@app.route("/list",methods= ['GET'])   #查看所有文章列表  遍历方法学自csdn博客
def list():
    db_session = g.db   #通过全局变量g传入实例化db_session
    articles = db_session.query(Article).all()   #遍历数据库
    result = []   #将结果存在数组中
    content = {}   #显示文章的内容
    for article in articles:   #通过循环将遍历文章表的内容存在数组中
        content = {'name': article.name, 'author': article.user.name, 'content': article.content, }
        result.append(content)
    return jsonify(result)   #返回json格式


@app.route("/details",methods= ['GET'])   #查看一篇文章详情
def details():
    name = request.args.get('name')
    db_session = g.db   #通过全局变量g传入实例化db_session
    article = db_session.query(Article).filter(Article.name == name).first()
    if article is None:   #查询不到显示无效名字
        return jsonify("Invalid name!")
    content = article.content

    comments = db_session.query(Comment).filter(Comment.article_id == article.id).all()  #查询该文章所有评论
    result = [{"article": content}]   #result返回 第一项是文章内容 其余项为评论
    com_details = {}
    if comments is None:
        pass
    else:
        for comment in comments:
            com_details = {"user_id":comment.com_author_id, "content":comment.content}
            result.append(com_details)   #查询到所有评论

    return jsonify(result)   #返回json格式


@app.route("/comment",methods=['POST'])   #发表文章
def add_comment():
    name = request.args.get('name')   #存储http请求中的输入
    content = request.args.get('content')
    db_session = g.db
    article = db_session.query(Article).filter(Article.name == name).first()
    if article is None:   #查询不到显示无效名字
        return jsonify("Invalid name!")
    article_id = article.id
    cur_user_id = g.info['id']   #通过全局变量g将发表评论作者ID保存起来
    new_comment = Comment(content = content,  article_id = article_id , com_author_id = cur_user_id )
    new_comment.article = db_session.query(Article).filter(Article.id == article_id).first()  #添加关联
    db_session.add(new_comment)   #加入数据库
    db_session.commit()   #提交到数据库
    return{   #返回json文件,
         "comment_content": new_comment.content,
         "article_name": article.name,
    }


@app.route("/delComment",methods= ['GET','POST'])   #删除文章评论
def del_comment():
    content = request.args.get('content')
    db_session = g.db
    comment = db_session.query(Comment).filter(Comment.content == content).first()   #查询该评论
    if comment is None:  # 查询不到显示无效名字
        return jsonify("Invalid comment!")
    user_id = g.info['id']
    if user_id == comment.com_author_id:   #只有评论作者可以删除评论
        db_session.delete(comment)   #从数据库中删除
        db_session.commit()   #提交到数据库
        return jsonify("The comment "+comment.content +" has been deleted")
    else:
        return jsonify("You can't delete other people's comment!")
