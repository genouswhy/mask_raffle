from playwright.sync_api import sync_playwright
import time
import os

def test_raffle_page():
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=False)  # 设置为False可以看到浏览器窗口
        page = browser.new_page()
        
        # 访问网页
        print("正在打开网页...")
        page.goto('http://localhost:5789/')
        
        # 等待页面加载
        page.wait_for_load_state('networkidle')
        time.sleep(2)
        
        # 检查倒计时元素
        print("检查倒计时元素...")
        countdown_days = page.locator('#days')
        countdown_hours = page.locator('#hours')
        countdown_minutes = page.locator('#minutes')
        countdown_seconds = page.locator('#seconds')
        
        # 打印倒计时信息
        if countdown_days.is_visible():
            print(f"天数显示: {countdown_days.text_content()}")
            print(f"小时显示: {countdown_hours.text_content()}")
            print(f"分钟显示: {countdown_minutes.text_content()}")
            print(f"秒数显示: {countdown_seconds.text_content()}")
        else:
            print("倒计时元素不可见!")
        
        # 截图保存
        print("保存页面截图...")
        screenshot_path = os.path.join(os.getcwd(), 'raffle_screenshot.png')
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"截图保存在: {screenshot_path}")
        
        # 检查页面样式
        countdown_card = page.locator('.countdown-card')
        card_background = countdown_card.evaluate('el => window.getComputedStyle(el).background')
        print(f"倒计时卡片背景样式: {card_background}")
        
        # 暂停一会儿，观察页面
        time.sleep(5)
        
        # 关闭浏览器
        browser.close()

if __name__ == "__main__":
    test_raffle_page() 