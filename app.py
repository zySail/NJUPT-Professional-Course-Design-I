from flask import Flask, jsonify
import base64, hmac, time
from urllib.parse import quote, urlencode
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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

# 你的设备信息，统一写这里方便维护
USER_ID = '452794'
ACCESS_KEY = 'qfkNg6nPlQSS58K7XzjPvZVKt4HKofWqhkfnACZEesv9D8C4NigcTkjTMiJmUOqq'
PRODUCT_ID = 'QnTH9lJULe'
DEVICE_NAME = 'd1'

@app.route('/api/device-data')
def get_device_data():
    api_url = f'http://iot-api.heclouds.com/thingmodel/query-device-property?product_id={PRODUCT_ID}&device_name={DEVICE_NAME}'
    auth_token = token(USER_ID, ACCESS_KEY)
    headers = {'Authorization': auth_token}

    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        return jsonify({'code': -1, 'msg': f'HTTP error {response.status_code}'}), 500

    data = response.json()
    if data['code'] != 0:
        return jsonify({'code': -1, 'msg': data['msg']}), 500

    return jsonify({
        'code': 0,
        'data': [
            {
                'identifier': item['identifier'],
                'name': item.get('name', item['identifier']),
                'value': item['value']
            }
            for item in data['data']
        ]
    })

@app.route('/api/device-data/history')
def get_device_history():
    # 获取近1小时数据，单位毫秒时间戳
    end_time = int(time.time() * 1000)
    start_time = end_time - 3600 * 1000

    identifiers = ['co2', 'temp', 'pm25', 'light']
    base_url = 'http://iot-api.heclouds.com/thingmodel/query-device-property-history'
    result_data = {
        'times': [],
        'co2': [],
        'temp': [],
        'pm25': [],
        'light': [],
        'code': 0
    }

    for idx, identifier in enumerate(identifiers):
        params = {
            'product_id': PRODUCT_ID,
            'device_name': DEVICE_NAME,
            'identifier': identifier,
            'start_time': start_time,
            'end_time': end_time,
            'limit': 10,
            'sort': 'desc'
        }
        api_url = base_url + '?' + urlencode(params)
        headers = {'Authorization': token(USER_ID, ACCESS_KEY)}

        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            return jsonify({'code': -1, 'msg': f'HTTP error {response.status_code}'}), 500

        data = response.json()
        if data.get('code') != 0:
            return jsonify({'code': -1, 'msg': data.get('msg')}), 500

        history_list = data['data']['list']
        if idx == 0:
            # 时间戳列表，倒序改正为升序
            result_data['times'] = list(reversed([str(item['time']) for item in history_list]))

        # 保存数据，倒序转升序
        result_data[identifier] = list(reversed([float(item['value']) for item in history_list]))

    return jsonify(result_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
