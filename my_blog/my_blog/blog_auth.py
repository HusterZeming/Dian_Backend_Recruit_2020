import jwt
import datetime   #过期时间  默认20分钟
from jwt import exceptions

SALT = 'iv$jfa$#%sd#%$,/$%$@^ji&fj^%^aif*^&&jfj&dos>>??*23'   #盐值

def create_token(payload, timeout=20):   #copy自github
    headers = {
        'typ': 'jwt',   #类型 jwt
        'alg': 'HS256'   #加密方法 哈希256
    }
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=timeout)
    #timeout过期时间 默认20分钟
    result = jwt.encode(payload=payload, key=SALT, algorithm="HS256", headers=headers).decode('utf-8')
    #encode函数生成token
    return result

def parse_payload(token):   #校验传入的token
    result = {'status': False,
              'data': None,
              'error': None,
              }
    try:
        verified_payload = jwt.decode(token, SALT, True)   #decode函数解码token
        result['status'] = True
        result['data'] = verified_payload   #payload
    except exceptions.ExpiredSignatureError:
        result['error'] = 'token已失效'
    except jwt.DecodeError:
        result['error'] = 'token认证失败'
    except jwt.InvalidTokenError:
        result['error'] = '非法的token'
    return result
