from flask import Flask
from flask import request   #导入request模块
from flask import jsonify   #导入jsonify模块用来返回json数据
from my_blog.blog_auth import create_token, parse_payload   #导入登录验证模块
import hashlib   #导入哈希模块
from my_blog.models import *   #导入模型
from my_blog import app
from my_blog.config import dbFactory

@app.route('/admin/doReg',methods=['POST'])   #注册
def doReg():
    blog_type = request.args.get('blog_type')   #前端传递blog_type
    db_session = dbFactory(blog_type)   #动态建立数据库 dbFactory由my_blog.config传入

    name = request.args.get('name')  # 存储http请求中的输入
    email = request.args.get('email')

    cur_user = db_session.query(User).filter(User.name == name).first()  # 判断用户是否已经存在
    if cur_user is None:
        pass
    else:
        return jsonify("User already exists!")   #如果用户存在，返回“用户已存在”

    cur_user = db_session.query(User).filter(User.email == email).first()   #判断邮箱是否已经存在
    if cur_user is None:
        pass
    else:
        return jsonify("Email already exists!")   #如果邮箱存在，返回“邮箱已存在”
    '''
    这两个重复的验证是在没找到好的封装方法，数据库查询操作写法比较刻板
    '''

    password = hashlib.md5(request.args.get('password').encode("utf-8"))  # 存储密码（MD5加密）
    hash_md5 = password.hexdigest()
    new_user = User(name=name, email=email, password=hash_md5)  #存储新用户

    db_session.add(new_user)  # 加入数据库
    db_session.commit()  # 提交到数据库

    return {  # 返回json数据
        "user_name": new_user.name,
        "user_email": new_user.email,
    }


@app.route('/admin/doLogin',methods=['GET','POST'])   #登陆
def doLogin():
    blog_type = request.args.get('blog_type')  # 前端传递blog_type
    db_session = dbFactory(blog_type)  #动态建立数据库连接 dbFactory由my_blog.config传入

    name = request.args.get('name')   #存储http请求中的输入
    password = hashlib.md5(request.args.get('password').encode("utf-8"))   #将密码进行MD5处理化进行验证
    hash_md5 = password.hexdigest()
    user = db_session.query(User).filter(User.name == name).first()   # 检测用户和密码是否正确
    if user is None:   #查询不到显示无效用户
        return jsonify("Invalid user!")
    elif user.password == hash_md5:   # 用户名和密码正确，生成token并返回，不正确显示错误
        token = create_token({'id': user.id, 'area': blog_type})
        return jsonify({'status': True, 'token': token})
    else:
        return jsonify({'status': False, 'error': '用户名或密码错误', 'pass': request.args.get('password')})
