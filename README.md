# Zeeverse Genesis Mask 抽奖实时监控

## 功能简介
- 实时监控社区钱包 Genesis Mask 捐赠
- 展示捐赠人地址（Opensea超链接）、ENS、mask数量、最近捐赠时间、抽中1/2/3个概率
- 前后端一体，支持自动刷新、双语切换、倒计时显示

## 部署与运行

### 本地开发运行

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 配置环境变量（可选）

- `ETHERSCAN_API_KEY`：以太坊Etherscan API Key（已内置默认值）
- `RAFFLE_DEADLINE`：抽奖截止时间（默认2025-04-16T10:00:00Z）
- `RAFFLE_LIVE_DRAW`：开奖时间（默认2025-04-16T12:00:00Z）

3. 启动服务

```bash
python app.py
```

4. 访问前端

浏览器打开 http://localhost:8080/

### 云端部署

项目已配置好多种云平台的部署文件，详细部署指南请查看：
- [部署指南(中文)](README-deploy-zh.md)
- [Deployment Guide(English)](README-deploy-en.md)

支持的部署平台包括：
- Render (推荐)
- Vercel
- Heroku
- PythonAnywhere
- 自定义服务器

## 说明
- 后端每5分钟自动同步链上捐赠数据
- 支持手动刷新获取最新数据
- ENS解析速度依赖外部API
- 概率为理论值，按mask数量分配抽奖权 