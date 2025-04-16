import os
import time
import threading
import json
from flask import Flask, jsonify, send_from_directory
import requests

ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY', 'B45FXGBS87F2JNV1A1SNQU7MWYMK3X5N3C')
COMMUNITY_WALLET = '0x4d3Cb2F6B1b73578C07c630F55A89D433722Bc06'.lower()

app = Flask(__name__)

# 数据缓存
cache = {
    'donors': [],
    'last_update': 0
}

def fetch_mask_donations():
    url = f'https://api.etherscan.io/api?module=account&action=tokennfttx&address={COMMUNITY_WALLET}&page=1&offset=100&sort=desc&apikey={ETHERSCAN_API_KEY}'
    resp = requests.get(url).json()
    result = resp.get('result', [])
    donations = {}
    for tx in result:
        if tx['to'].lower() == COMMUNITY_WALLET:
            donor = tx['from'].lower()
            token_id = tx['tokenID']
            timestamp = int(tx['timeStamp'])
            if donor not in donations:
                donations[donor] = {
                    'address': donor,
                    'ens': None,  # 不再使用Web3解析ENS
                    'count': 0,
                    'last_time': 0,
                    'token_ids': []
                }
            donations[donor]['count'] += 1
            donations[donor]['last_time'] = max(donations[donor]['last_time'], timestamp)
            donations[donor]['token_ids'].append(token_id)
    return list(donations.values())

def update_cache():
    while True:
        try:
            donors = fetch_mask_donations()
            cache['donors'] = donors
            cache['last_update'] = int(time.time())
            print(f"更新缓存: 找到 {len(donors)} 个捐赠者")
        except Exception as e:
            print('Error updating cache:', e)
        time.sleep(60)

@app.route('/api/donors')
def api_donors():
    # 计算概率
    donors = cache['donors']
    total = sum(d['count'] for d in donors)
    for d in donors:
        n = d['count']
        d['prob_1'] = round(1 - ((total-n)/total)**9, 6) if total > 0 else 0
        d['prob_2'] = round(1 - ((total-n)/total)**9 - 9*((n/total)*((total-n)/total)**8), 6) if total > 0 else 0
        d['prob_3'] = round(1 - ((total-n)/total)**9 - 9*((n/total)*((total-n)/total)**8) - 36*((n/total)**2)*((total-n)/total)**7, 6) if total > 0 else 0
    return jsonify({'donors': donors, 'last_update': cache['last_update']})

@app.route('/')
def root():
    return send_from_directory('.', 'index.html')

@app.route('/index.html')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    threading.Thread(target=update_cache, daemon=True).start()
    app.run(host='0.0.0.0', port=5678, debug=True) 