import os
import time
import threading
import json
import requests
from flask import Flask, jsonify, send_from_directory

ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY', 'B45FXGBS87F2JNV1A1SNQU7MWYMK3X5N3C')
COMMUNITY_WALLET = '0x4d3Cb2F6B1b73578C07c630F55A89D433722Bc06'.lower()
RAFFLE_DEADLINE = "2025-04-16T10:00:00Z"  # 抽奖截止时间，设置为未来日期
RAFFLE_LIVE_DRAW = "2025-04-16T12:00:00Z"  # 开奖时间

app = Flask(__name__)

# 数据缓存
cache = {
    'donors': [],
    'last_update': 0
}

def get_ens_for_address(address):
    """使用外部API获取ENS域名"""
    try:
        # 使用以太坊public API
        url = f"https://api.ensideas.com/ens/resolve/{address}"
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            data = response.json()
            if 'name' in data and data['name']:
                return data['name']
    except Exception as e:
        print(f"ENS解析错误: {e}")
    return None

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
                    'ens': None,
                    'count': 0,
                    'last_time': 0,
                    'token_ids': []
                }
            donations[donor]['count'] += 1
            donations[donor]['last_time'] = max(donations[donor]['last_time'], timestamp)
            if token_id not in donations[donor]['token_ids']:
                donations[donor]['token_ids'].append(token_id)
    
    # 为每个捐赠者获取ENS
    donor_list = list(donations.values())
    for donor in donor_list:
        if not donor['ens']:  # 如果没有ENS，尝试获取
            donor['ens'] = get_ens_for_address(donor['address'])
    
    return donor_list

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
    
    # 添加调试日志
    print(f"发送倒计时: {RAFFLE_DEADLINE}")
    
    return jsonify({
        'donors': donors, 
        'last_update': cache['last_update'],
        'total_masks': total,
        'total_donors': len(donors),
        'raffle_deadline': RAFFLE_DEADLINE,
        'raffle_live_draw': RAFFLE_LIVE_DRAW
    })

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """手动刷新数据"""
    try:
        donors = fetch_mask_donations()
        cache['donors'] = donors
        cache['last_update'] = int(time.time())
        return jsonify({"status": "success", "message": "Data refreshed successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/')
def root():
    return send_from_directory('.', 'enhanced.html')

@app.route('/enhanced.html')
def index():
    return send_from_directory('.', 'enhanced.html')

if __name__ == '__main__':
    threading.Thread(target=update_cache, daemon=True).start()
    app.run(host='0.0.0.0', port=5789, debug=True) 