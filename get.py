import base64
import hmac
import time
from urllib.parse import quote
import requests


# 生成 Token 函数
def fix_base64_padding(s):
    return s + '=' * (-len(s) % 4)


def token(user_id, access_key):
    version = '2022-05-01'
    res = f'userid/{user_id}'
    et = str(int(time.time()) + 3600)
    method = 'sha1'

    key = base64.b64decode(fix_base64_padding(access_key))
    org = f'{et}\n{method}\n{res}\n{version}'
    sign_b = hmac.new(key=key, msg=org.encode(), digestmod=method)
    sign = base64.b64encode(sign_b.digest()).decode()
    sign = quote(sign, safe='')
    res = quote(res, safe='')

    return f'version={version}&res={res}&et={et}&method={method}&sign={sign}'


# 获取并处理数据函数
def get_device_data():
    # 基本信息
    user_id = '452809'
    access_key = 'i4VKCAn5AWl3rlRS/qPo9g5GszzqtrbXfDLYiuEUFSfAriYAPr6Lg1iLlROuXl6I'
    api_url = 'http://iot-api.heclouds.com/thingmodel/query-device-property?product_id=1KW8SyPzsI&device_name=sensor1'

    # 构建 Header
    auth_token = token(user_id, access_key)
    headers = {
        'Authorization': auth_token
    }

    # 发送请求
    response = requests.get(api_url, headers=headers)

    if response.status_code != 200:
        print(f'请求失败，状态码：{response.status_code}')
        return

    data = response.json()

    if data['code'] != 0:
        print(f"API 错误：{data['msg']}")
        return

    device_data = data['data']  # 实际数据是直接在 data 字段中

    # 提取 identifier 和 value
    print("传感器数据：")
    for item in device_data:
        identifier = item['identifier']
        value = item['value']
        name = item.get('name', identifier)
        print(f"{name}（{identifier}）: {value}")


if __name__ == '__main__':
    get_device_data()
