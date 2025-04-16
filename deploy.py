import os
import json
import time
import threading
from flask import Flask, jsonify, send_from_directory, render_template_string, make_response
import requests
from datetime import datetime

# 环境变量配置
ETHERSCAN_API_KEY = os.environ.get('ETHERSCAN_API_KEY', 'B45FXGBS87F2JNV1A1SNQU7MWYMK3X5N3C')
COMMUNITY_WALLET = '0x4d3Cb2F6B1b73578C07c630F55A89D433722Bc06'.lower()
RAFFLE_DEADLINE = os.environ.get('RAFFLE_DEADLINE', "2025-04-16T10:00:00Z")  # 抽奖截止时间
RAFFLE_LIVE_DRAW = os.environ.get('RAFFLE_LIVE_DRAW', "2025-04-16T12:00:00Z")  # 开奖时间

app = Flask(__name__, static_folder='static')

# 缓存存储
cache = {
    'donors': [],
    'history': [],
    'last_update': 0,
    'html_content': None
}

# 基础HTML模板
DEFAULT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mask Network Raffle</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            text-align: center;
        }
        h1 {
            color: #1c60c7;
        }
    </style>
</head>
<body>
    <h1>Mask Network Raffle</h1>
    <p>The raffle application is currently unavailable.</p>
    <p>Please check back later.</p>
    <p>API endpoints are still available at: <a href="/api/donors">/api/donors</a></p>
</body>
</html>
"""

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
        url = f'https://api.etherscan.io/api?module=account&action=tokennfttx&address={COMMUNITY_WALLET}&page=1&offset=200&sort=desc&apikey={ETHERSCAN_API_KEY}'
        resp = requests.get(url).json()
        result = resp.get('result', [])
        donations = {}
        history_items = []
        
        for tx in result:
            if tx['to'].lower() == COMMUNITY_WALLET:
                donor = tx['from'].lower()
                token_id = tx['tokenID']
                timestamp = int(tx['timeStamp'])
                tx_hash = tx['hash']
                
                # 为历史记录添加数据
                history_item = {
                    'tx_hash': tx_hash,
                    'token_id': token_id,
                    'from_address': donor,
                    'to_address': COMMUNITY_WALLET,
                    'timestamp': timestamp,
                    'date': datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                    'ens': None
                }
                history_items.append(history_item)
                
                # 处理总体捐赠统计
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
        
        # 获取ENS并更新
        donor_list = list(donations.values())
        address_ens_map = {}
        
        # 为每个唯一地址获取ENS
        all_addresses = set([d['address'] for d in donor_list])
        for address in all_addresses:
            ens = get_ens_for_address(address)
            if ens:
                address_ens_map[address] = ens
        
        # 更新捐赠者列表的ENS
        for donor in donor_list:
            donor['ens'] = address_ens_map.get(donor['address'])
        
        # 更新历史记录的ENS
        for item in history_items:
            item['ens'] = address_ens_map.get(item['from_address'])
        
        # 按时间排序历史记录（最新的在前）
        history_items.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return donor_list, history_items
    except Exception as e:
        print(f"获取捐赠数据出错: {e}")
        return [], []

def load_html_file(filename):
    """加载HTML文件，支持多个位置查找，如果找不到则返回默认HTML"""
    # 尝试多个可能的路径
    possible_paths = [
        filename,  # 当前目录
        f"./{filename}",  # 显式当前目录
        f"./static/{filename}",  # static目录
        f"../static/{filename}",  # 上级static目录
        f"/app/{filename}",  # 容器内常用路径
        f"/app/static/{filename}"  # 容器内static目录
    ]
    
    for path in possible_paths:
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"尝试读取 {path} 失败: {e}")
    
    print(f"警告: 无法找到 {filename}，使用默认HTML")
    return DEFAULT_HTML

def update_cache():
    """定期更新缓存"""
    while True:
        try:
            donors, history = fetch_mask_donations()
            cache['donors'] = donors
            cache['history'] = history
            cache['last_update'] = int(time.time())
            print(f"缓存已更新，共 {len(cache['donors'])} 个捐赠者, {len(cache['history'])} 条历史记录")
        except Exception as e:
            print(f"更新缓存出错: {e}")
        time.sleep(300)  # 5分钟更新一次

@app.route('/api/donors')
def api_donors():
    """API端点，返回捐赠数据"""
    try:
        # 尝试从缓存获取，如果缓存为空，则获取新数据
        if not cache['donors']:
            donors, history = fetch_mask_donations()
            cache['donors'] = donors
            cache['history'] = history
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

@app.route('/api/history')
def api_history():
    """API端点，返回历史捐赠数据"""
    try:
        # 尝试从缓存获取，如果缓存为空，则获取新数据
        if not cache['history']:
            donors, history = fetch_mask_donations()
            cache['donors'] = donors
            cache['history'] = history
            cache['last_update'] = int(time.time())
        
        return jsonify({
            'history': cache['history'],
            'last_update': cache['last_update'],
            'total_transactions': len(cache['history'])
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """手动刷新数据"""
    try:
        donors, history = fetch_mask_donations()
        cache['donors'] = donors
        cache['history'] = history
        cache['last_update'] = int(time.time())
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def root():
    """主页路由"""
    html_content = load_html_file("enhanced.html")
    if html_content == DEFAULT_HTML:
        # 如果enhanced.html不存在，尝试使用index.html
        html_content = load_html_file("index.html")
    
    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response

@app.route('/index.html')
def index_html():
    """index.html路由"""
    return root()

@app.route('/enhanced.html')
def enhanced_html():
    """enhanced.html路由"""
    return root()

@app.route('/static/<path:path>')
def serve_static(path):
    """提供静态文件"""
    try:
        return send_from_directory('static', path)
    except Exception as e:
        print(f"静态文件访问错误: {e}")
        try:
            return send_from_directory('.', path)
        except Exception:
            return f"文件 {path} 不存在", 404

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
    
    # 预加载数据和HTML
    donors, history = fetch_mask_donations()
    cache['donors'] = donors
    cache['history'] = history
    cache['last_update'] = int(time.time())
    
    # 获取端口，用于云平台部署
    port = int(os.environ.get('PORT', 8080))
    print(f"启动服务器在端口: {port}，按Ctrl+C终止")
    app.run(host='0.0.0.0', port=port) 