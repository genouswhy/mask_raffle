# Zeeverse Genesis Mask Raffle Monitor - Deployment Guide

This project can be deployed on various free/paid platforms. Below are instructions for several major deployment methods.

## Project Overview

- Real-time monitoring of the Zeeverse Genesis Mask raffle activity
- Displays donors, ENS domains, probability information, etc.
- Features countdown timer, bilingual interface, and manual refresh

## Deployment Options

### 1. Render (Recommended)

[Render](https://render.com) offers free web services.

1. Sign up for a Render account
2. Click "New" > "Web Service"
3. Connect your GitHub repository
4. Set up:
   - Name: `mask-raffle`
   - Build Command: `pip install -r requirements-deploy.txt`
   - Start Command: `gunicorn deploy:app`
5. Click "Create Web Service"

Render will automatically recognize the `render.yaml` file and deploy according to its configuration.

### 2. Vercel

[Vercel](https://vercel.com) provides free static websites and serverless functions.

1. Sign up for a Vercel account
2. Install Vercel CLI: `npm i -g vercel`
3. Run in the project directory: `vercel`
4. Follow the prompts to set up the project
5. After completion, visit the assigned URL

Vercel will deploy based on the `vercel.json` configuration file.

### 3. Heroku

[Heroku](https://heroku.com) offers free web application hosting.

1. Sign up for a Heroku account
2. Install Heroku CLI
3. Run the following commands:
   ```
   heroku login
   heroku create mask-raffle
   git push heroku main
   ```

Heroku will deploy based on the `Procfile` file.

### 4. PythonAnywhere

[PythonAnywhere](https://www.pythonanywhere.com/) provides free Python application hosting.

1. Sign up for a PythonAnywhere account
2. Create a web application
3. Set the WSGI configuration file to point to `wsgi.py`
4. Upload all project files
5. Install dependencies: `pip install -r requirements-deploy.txt`

### 5. Custom Server

If you have your own server, you can:

1. Clone the code to your server
2. Install dependencies: `pip install -r requirements-deploy.txt`
3. Configure Nginx as a reverse proxy
4. Use Supervisor or Systemd to manage the application
5. Start the application: `gunicorn deploy:app`

## Environment Variables

- `ETHERSCAN_API_KEY`: Etherscan API key
- `PORT`: Application port (default 8080)

## Notes

- Ensure the `enhanced.html` file is in the same directory
- ENS resolution may be slower on some platforms
- Inability to resolve ENS does not affect core functionality 