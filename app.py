from flask import Flask, jsonify, render_template
import base64, hmac, time, requests
from urllib.parse import quote

app = Flask(__name__)

# === token 生成 ===
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


@app.route("/api/data")
def get_data():
    user_id = '452809'
    access_key = 'i4VKCAn5AWl3rlRS/qPo9g5GszzqtrbXfDLYiuEUFSfAriYAPr6Lg1iLlROuXl6I'
    api_url = 'http://iot-api.heclouds.com/thingmodel/query-device-property?product_id=1KW8SyPzsI&device_name=sensor1'
    headers = {'Authorization': generate_api_token(user_id, access_key)}
    try:
        response = requests.get(api_url, headers=headers)
        data = response.json()
        if data['code'] == 0:
            return jsonify(data['data'])  # 返回 data 列表
        else:
            return jsonify({"error": data['msg']})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
