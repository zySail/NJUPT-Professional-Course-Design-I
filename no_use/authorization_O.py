import base64
import hmac
import time
from urllib.parse import quote


def token(user_id, access_key):
    version = '2022-05-01'
    res = 'userid/%s' % user_id
    # 用户自定义token过期时间
    et = str(int(time.time()) + 3600)
    # 签名方法，支持md5、sha1、sha256
    method = 'sha1'
    # 对access_key进行decode
    key = base64.b64decode(access_key)
    # 计算sign
    org = et + '\n' + method + '\n' + res + '\n' + version
    sign_b = hmac.new(key=key, msg=org.encode(), digestmod=method)
    sign = base64.b64encode(sign_b.digest()).decode()
    # value 部分进行url编码，method/res/version值较为简单无需编码
    sign = quote(sign, safe='')
    res = quote(res, safe='')
    # token参数拼接
    token = 'version=%s&res=%s&et=%s&method=%s&sign=%s' % (version, res, et, method, sign)

    return token


if __name__ == '__main__':
    user_id = '1KW8SyPzsI'
    access_key = '69ur+wEHozXDT+cxx6Wz798phelzVzGBtb2/XU'
    # access_key = 'i4VKCAn5AWl3rlRS/qPo9g5GszzqtrbXfDLYiuEUFSfAriYAPr6Lg1iLlROuXl6I'
    # access_key ='UGdHR0VPUHZ5NGsxQ0Vpa2lUYm9QeU8ybmlJS0xqVW0='

    print(token(user_id, access_key))