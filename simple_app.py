from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>测试服务正常运行</h1>"

@app.route('/test.html')
def test():
    return send_from_directory('.', 'test.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 