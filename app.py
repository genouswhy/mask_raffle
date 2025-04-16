import os
import json
import threading
import time
from flask import Flask, jsonify
import requests

# 环境变量配置
ETHERSCAN_API_KEY = os.environ.get('ETHERSCAN_API_KEY', 'B45FXGBS87F2JNV1A1SNQU7MWYMK3X5N3C')
COMMUNITY_WALLET = '0x4d3Cb2F6B1b73578C07c630F55A89D433722Bc06'.lower()
RAFFLE_DEADLINE = os.environ.get('RAFFLE_DEADLINE', "2025-04-16T10:00:00Z")  # 抽奖截止时间
RAFFLE_LIVE_DRAW = os.environ.get('RAFFLE_LIVE_DRAW', "2025-04-16T12:00:00Z")  # 开奖时间

app = Flask(__name__)

# 缓存存储
cache = {
    'donors': [],
    'last_update': 0
}

def get_ens_for_address(address):
    """使用外部API获取ENS域名"""
    try:
        url = f"https://api.ensideas.com/ens/resolve/{address}"
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            data = response.json()
            if 'name' in data and data['name']:
                return data['name']
    except Exception:
        pass
    return None

def fetch_mask_donations():
    """获取捐赠数据"""
    try:
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
        
        # 获取ENS
        donor_list = list(donations.values())
        for donor in donor_list:
            if not donor['ens']:
                donor['ens'] = get_ens_for_address(donor['address'])
        
        return donor_list
    except Exception as e:
        print(f"获取捐赠数据出错: {e}")
        return []

def update_cache():
    """定期更新缓存"""
    while True:
        try:
            cache['donors'] = fetch_mask_donations()
            cache['last_update'] = int(time.time())
            print(f"缓存已更新，共 {len(cache['donors'])} 个捐赠者")
        except Exception as e:
            print(f"更新缓存出错: {e}")
        time.sleep(300)  # 5分钟更新一次

@app.route('/api/donors')
def api_donors():
    """API端点，返回捐赠数据"""
    try:
        # 尝试从缓存获取，如果缓存为空，则获取新数据
        if not cache['donors']:
            cache['donors'] = fetch_mask_donations()
            cache['last_update'] = int(time.time())
        
        # 计算概率
        donors = cache['donors']
        total = sum(d['count'] for d in donors)
        for d in donors:
            n = d['count']
            d['prob_1'] = round(1 - ((total-n)/total)**9, 6) if total > 0 else 0
            d['prob_2'] = round(1 - ((total-n)/total)**9 - 9*((n/total)*((total-n)/total)**8), 6) if total > 0 else 0
            d['prob_3'] = round(1 - ((total-n)/total)**9 - 9*((n/total)*((total-n)/total)**8) - 36*((n/total)**2)*((total-n)/total)**7, 6) if total > 0 else 0
        
        return jsonify({
            'donors': donors, 
            'last_update': cache['last_update'],
            'total_masks': total,
            'total_donors': len(donors),
            'raffle_deadline': RAFFLE_DEADLINE,
            'raffle_live_draw': RAFFLE_LIVE_DRAW
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """手动刷新数据"""
    try:
        cache['donors'] = fetch_mask_donations()
        cache['last_update'] = int(time.time())
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/healthz')
def health_check():
    """健康检查"""
    return jsonify({"status": "ok"})

@app.route('/_ah/health')
def google_health_check():
    """Google Cloud健康检查"""
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    # 启动后台线程
    threading.Thread(target=update_cache, daemon=True).start()
    
    # 获取端口，用于云平台部署
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port) 