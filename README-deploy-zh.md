# Zeeverse Genesis Mask 抽奖监控 - 部署指南

本项目可以部署在各种免费/付费平台上。以下是几种主要部署方法的说明。

## 项目概述

- 实时监控 Zeeverse Genesis Mask 抽奖活动
- 显示捐赠者、ENS域名、概率信息等
- 具有倒计时、双语界面和手动刷新功能

## 部署选项

### 1. Render（推荐）

[Render](https://render.com) 提供免费的Web服务。

1. 注册Render账户
2. 点击"New" > "Web Service"
3. 连接您的GitHub仓库
4. 设置:
   - 名称: `mask-raffle`
   - 构建命令: `pip install -r requirements-deploy.txt`
   - 启动命令: `gunicorn deploy:app`
5. 点击"Create Web Service"

Render将自动识别`render.yaml`文件并根据其配置进行部署。

### 2. Vercel

[Vercel](https://vercel.com) 提供免费的静态网站和无服务器功能。

1. 注册Vercel账户
2. 安装Vercel CLI: `npm i -g vercel`
3. 在项目目录中运行: `vercel`
4. 按照提示设置项目
5. 完成后，访问分配的URL

Vercel将根据`vercel.json`配置文件进行部署。

### 3. Heroku

[Heroku](https://heroku.com) 提供免费的Web应用程序托管。

1. 注册Heroku账户
2. 安装Heroku CLI
3. 运行以下命令:
   ```
   heroku login
   heroku create mask-raffle
   git push heroku main
   ```

Heroku将根据`Procfile`文件进行部署。

### 4. PythonAnywhere

[PythonAnywhere](https://www.pythonanywhere.com/) 提供免费的Python应用程序托管。

1. 注册PythonAnywhere账户
2. 创建Web应用程序
3. 将WSGI配置文件指向`wsgi.py`
4. 上传所有项目文件
5. 安装依赖项: `pip install -r requirements-deploy.txt`

### 5. 自定义服务器

如果您有自己的服务器，您可以:

1. 将代码克隆到您的服务器
2. 安装依赖项: `pip install -r requirements-deploy.txt`
3. 配置Nginx作为反向代理
4. 使用Supervisor或Systemd管理应用程序
5. 启动应用程序: `gunicorn deploy:app`

## 环境变量

- `ETHERSCAN_API_KEY`: Etherscan API密钥
- `PORT`: 应用程序端口（默认8080）

## 注意事项

- 确保`enhanced.html`文件在同一目录中
- 在某些平台上ENS解析可能较慢
- 无法解析ENS不会影响核心功能 