import paho.mqtt.client as mqtt
import json
import time
import random
import base64
import hmac
from urllib.parse import quote

# 生成token函数，跟你给的官方示例一样
def generate_token(product_id, access_key, device_name):
    version = '2018-10-31'
    res = f'products/{product_id}/devices/{device_name}'
    et = str(int(time.time()) + 3600)  # 1小时后过期
    method = 'sha1'
    key = base64.b64decode(access_key)
    org = et + '\n' + method + '\n' + res + '\n' + version
    sign_b = hmac.new(key=key, msg=org.encode(), digestmod=method)
    sign = base64.b64encode(sign_b.digest()).decode()
    sign = quote(sign, safe='')
    res = quote(res, safe='')
    token = f'version={version}&res={res}&et={et}&method={method}&sign={sign}'
    return token

# 产品ID、设备名和密钥，需要替换成你自己的
product_id = "QnTH9lJULe"
device_name = "d1"
access_key = "Q3lhaWdLRTJydndwemk0SFRPM2FmMW53Q28wMDZJbkQ="

# MQTT服务器和端口
host = "mqtts.heclouds.com"
port = 1883

# 生成token作为密码
password = generate_token(product_id, access_key, device_name)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("连接成功")
    else:
        print(f"连接失败，返回码 {rc}")

client = mqtt.Client(client_id=device_name)
client.username_pw_set(username=product_id, password=password)
client.on_connect = on_connect

client.connect(host, port, 60)
client.loop_start()

while True:
    payload = {
        "temp": round(random.uniform(-20, 60), 2),
        "light": random.randint(0, 1000),
        "pm25": round(random.uniform(0, 500), 2),
        "co2": round(random.uniform(350, 5000), 2)
    }
    onenet_data = {
        "id": "123",  # 可改为动态值，例如 str(int(time.time()))
        "version": "1.0",
        "params": {
            k: {"value": v} for k, v in payload.items()
        }
    }

    topic = f"$sys/{product_id}/{device_name}/thing/property/post"
    client.publish(topic, json.dumps(onenet_data))
    print("上传成功：", onenet_data)
    time.sleep(10)
