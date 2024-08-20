import subprocess
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def start_chrome_with_debugging():
    chrome_path = r"C:\Users\Xingwei-Tech\AppData\Local\Google\Chrome\Application\chrome.exe"
    
    # 启动 Chrome 进程
    chrome_process = subprocess.Popen([
        chrome_path,
        '--remote-debugging-port=9222',
        '--user-data-dir=C:/ChromeDevSession'
    ])

    # 等待 Chrome 启动，检查进程状态
    max_wait_time = 10  # 最大等待时间 10 秒
    start_time = time.time()
    
    while chrome_process.poll() is None:
        if time.time() - start_time > max_wait_time:
            print("Chrome 启动超时")
            break
        time.sleep(0.5)  # 每 0.5 秒检查一次

    print("Chrome 已启动")

def search_keyword(keyword):
    options = webdriver.ChromeOptions()
    options.debugger_address = "localhost:9222"
    
    driver = webdriver.Chrome(options=options)
    
    driver.get("https://www.1688.com")
    
    # 使用 WebDriverWait 等待页面加载完成和搜索框出现
    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "alisearch-input"))
        )
        print("搜索框已找到")
        
        # 使用 JavaScript 设置搜索框的值并提交
        driver.execute_script("arguments[0].value = arguments[1];", search_box, keyword)
        driver.execute_script("arguments[0].form.submit();", search_box)
        
        print("搜索框已通过 JavaScript 成功输入关键词并提交表单")
    except Exception as e:
        print(f"搜索框加载失败: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_chrome_with_debugging()
    search_keyword('交换机')
