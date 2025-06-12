import base64
import hmac
import time
import random
import json
import threading
import requests
from urllib.parse import quote
import paho.mqtt.client as mqtt


# ========== MQTT 上传部分 ==========
def generate_mqtt_token(product_id, access_key, device_name):
    version = '2018-10-31'
    res = f'products/{product_id}/devices/{device_name}'
    et = str(int(time.time()) + 3600)
    method = 'sha1'
    key = base64.b64decode(access_key)
    org = et + '\n' + method + '\n' + res + '\n' + version
    sign_b = hmac.new(key=key, msg=org.encode(), digestmod=method)
    sign = base64.b64encode(sign_b.digest()).decode()
    sign = quote(sign, safe='')
    res = quote(res, safe='')
    return f'version={version}&res={res}&et={et}&method={method}&sign={sign}'


def upload_loop():
    product_id = "1KW8SyPzsI"
    device_name = "sensor1"
    access_key = "UGdHR0VPUHZ5NGsxQ0Vpa2lUYm9QeU8ybmlJS0xqVW0="
    host = "mqtts.heclouds.com"
    port = 1883

    password = generate_mqtt_token(product_id, access_key, device_name)
    client = mqtt.Client(client_id=device_name)
    client.username_pw_set(username=product_id, password=password)

    def on_connect(client, userdata, flags, rc):
        print("【MQTT】连接成功" if rc == 0 else f"【MQTT】连接失败，返回码 {rc}")

    client.on_connect = on_connect
    client.connect(host, port, 60)
    client.loop_start()

    def publish_data():
        payload = {
            "temp": round(random.uniform(-20, 60), 2),
            "light": random.randint(0, 1000),
            "pm25": round(random.uniform(0, 500), 2),
            "co2": round(random.uniform(350, 5000), 2)
        }

        onenet_data = {
            "id": str(int(time.time())),
            "version": "1.0",
            "params": {
                k: {"value": v} for k, v in payload.items()
            }
        }

        topic = f"$sys/{product_id}/{device_name}/thing/property/post"
        client.publish(topic, json.dumps(onenet_data))
        print("【上传】成功：", onenet_data)
        threading.Timer(5, publish_data).start()

    publish_data()


# ========== API 查询部分 ==========
def fix_base64_padding(s):
    return s + '=' * (-len(s) % 4)


def generate_api_token(user_id, access_key):
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


def get_device_data_loop():
    user_id = '452809'
    access_key = 'i4VKCAn5AWl3rlRS/qPo9g5GszzqtrbXfDLYiuEUFSfAriYAPr6Lg1iLlROuXl6I'
    api_url = 'http://iot-api.heclouds.com/thingmodel/query-device-property?product_id=1KW8SyPzsI&device_name=sensor1'
    auth_token = generate_api_token(user_id, access_key)
    headers = {'Authorization': auth_token}

    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            print(f"【查询】请求失败，状态码：{response.status_code}")
        else:
            data = response.json()
            if data['code'] != 0:
                print(f"【查询】API 错误：{data['msg']}")
            else:
                print("【查询】传感器数据：")
                for item in data['data']:
                    identifier = item['identifier']
                    value = item['value']
                    name = item.get('name', identifier)
                    print(f"  {name}（{identifier}）: {value}")
    except Exception as e:
        print(f"【查询】异常：{e}")

    threading.Timer(10, get_device_data_loop).start()


# ========== 程序入口 ==========
if __name__ == '__main__':
    upload_loop()         # 启动上传线程
    get_device_data_loop()  # 启动查询线程
