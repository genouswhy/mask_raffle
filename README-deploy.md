# Zeeverse Genesis Mask 抽奖监控 - 部署指南

这个项目可以部署在各种免费/付费平台上。以下是几种主要部署方式的说明。

## 项目简介

- 实时监控Zeeverse Genesis Mask抽奖活动
- 显示捐赠者、ENS域名、概率等信息
- 支持倒计时、双语界面和手动刷新

## 部署选项

### 1. Render (推荐)

[Render](https://render.com) 提供免费的Web服务。

1. 注册Render账号
2. 点击 "New" > "Web Service"
3. 连接你的GitHub仓库
4. 设置：
   - Name: `mask-raffle`
   - Build Command: `pip install -r requirements-deploy.txt`
   - Start Command: `gunicorn deploy:app`
5. 点击 "Create Web Service"

Render会自动识别`render.yaml`文件并按照其中的配置部署。

### 2. Vercel

[Vercel](https://vercel.com) 提供免费的静态网站和无服务器函数。

1. 注册Vercel账号
2. 安装Vercel CLI: `npm i -g vercel`
3. 在项目目录运行：`vercel`
4. 按照提示设置项目
5. 完成后，访问分配的URL

Vercel会根据`vercel.json`配置文件部署。

### 3. Heroku

[Heroku](https://heroku.com) 提供免费的Web应用托管。

1. 注册Heroku账号
2. 安装Heroku CLI
3. 运行以下命令:
   ```
   heroku login
   heroku create mask-raffle
   git push heroku main
   ```

Heroku会根据`Procfile`文件部署。

### 4. PythonAnywhere

[PythonAnywhere](https://www.pythonanywhere.com/) 提供免费的Python应用托管。

1. 注册PythonAnywhere账号
2. 创建Web应用
3. 设置WSGI配置文件指向`wsgi.py`
4. 上传所有项目文件
5. 安装依赖：`pip install -r requirements-deploy.txt`

### 5. 自定义服务器

如果你有自己的服务器，可以:

1. 克隆代码到服务器
2. 安装依赖：`pip install -r requirements-deploy.txt`
3. 使用Nginx配置反向代理
4. 使用Supervisor或Systemd管理应用
5. 启动应用：`gunicorn deploy:app`

## 环境变量

- `ETHERSCAN_API_KEY`: Etherscan API密钥
- `PORT`: 应用端口号（默认8080）

## 注意事项

- 确保`enhanced.html`文件位于同一目录
- ENS解析可能在某些平台上较慢
- 无法解析ENS不影响主要功能 