import base64
import hmac
import time
from urllib.parse import quote


def fix_base64_padding(s):
    return s + '=' * (-len(s) % 4)


def token(user_id, access_key):
    version = '2022-05-01'
    res = 'userid/%s' % user_id
    et = str(int(time.time()) + 3600)
    method = 'sha1'

    # 修复 base64 padding 并 decode
    key = base64.b64decode(fix_base64_padding(access_key))

    org = et + '\n' + method + '\n' + res + '\n' + version
    sign_b = hmac.new(key=key, msg=org.encode(), digestmod=method)
    sign = base64.b64encode(sign_b.digest()).decode()
    sign = quote(sign, safe='')
    res = quote(res, safe='')

    token = 'version=%s&res=%s&et=%s&method=%s&sign=%s' % (version, res, et, method, sign)
    return token


if __name__ == '__main__':
    user_id = '452809'
    access_key = 'i4VKCAn5AWl3rlRS/qPo9g5GszzqtrbXfDLYiuEUFSfAriYAPr6Lg1iLlROuXl6I'
    print(token(user_id, access_key))
