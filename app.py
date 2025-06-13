from flask import Flask, jsonify
import base64, hmac, time
from urllib.parse import quote
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
@app.route('/')
def index():
    return 'Flask 后端正在运行中 ✅'

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

@app.route('/api/device-data')
def get_device_data():
    user_id = '452794'
    access_key = 'qfkNg6nPlQSS58K7XzjPvZVKt4HKofWqhkfnACZEesv9D8C4NigcTkjTMiJmUOqq'
    api_url = 'http://iot-api.heclouds.com/thingmodel/query-device-property?product_id=QnTH9lJULe&device_name=d1'
    auth_token = token(user_id, access_key)
    headers = { 'Authorization': auth_token }
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
