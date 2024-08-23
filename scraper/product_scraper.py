import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import subprocess
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException


class ProductScraper:
    def __init__(self):
        self.chrome_path = r"C:\Users\Xingwei-Tech\AppData\Local\Google\Chrome\Application\chrome.exe"
        self.user_data_dir = "C:/ChromeDevSession"
        self.remote_debugging_port = 9222
        self.driver = None

    def start_chrome_with_debugging(self):
        self.chrome_process = subprocess.Popen([
            self.chrome_path,
            f'--remote-debugging-port={self.remote_debugging_port}',
            f'--user-data-dir={self.user_data_dir}'
        ])

        max_wait_time = 4  # 最大等待时间 4 秒
        start_time = time.time()
        
        while self.chrome_process.poll() is None:
            if time.time() - start_time > max_wait_time:
                print("Chrome 启动超时")
                break
            time.sleep(0.5)  # 每 0.5 秒检查一次

        print("Chrome 已启动")

    def stop_chrome_debugging(self):
        if self.chrome_process is not None:
            try:
                self.chrome_process.terminate()
                self.chrome_process.wait()
                print("Chrome 调试进程已终止")
            except Exception as e:
                print(f"终止 Chrome 调试进程失败: {e}")
        else:
            print("没有正在运行的 Chrome 调试进程")



    def scroll_to_bottom(self):
        scroll_increment = "document.body.scrollHeight * 0.1"
        total_scroll_time = 10  # 总滚动时间10秒
        interval = 1  # 每0.6秒滚动一次
        
        for _ in range(int(total_scroll_time / interval)):
            self.driver.execute_script(f"window.scrollBy(0, {scroll_increment});")
            time.sleep(interval)
        time.sleep(2)
        
    def wait_for_page_load_complete(self, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            print("Page loaded completely.")
        except TimeoutException:
            print("Page load timed out after waiting.")

    def get_product_details(self, url):
        self.driver.get(url)
        
        # 等待页面加载完成，等待时间可以根据需要调整
        time.sleep(3)  # 等待基础页面加载
        self.wait_for_page_load_complete()
        self.driver.execute_script(f"window.scrollBy(0, 100);")
    
        # 获取页面标题
        title = self.driver.title
        print(f"Page title: {title}")
        
        try:
            # 查找 class 为 "sku-wrapper-expend-button" 的元素
            expand_button = self.driver.find_element(By.CLASS_NAME, "sku-wrapper-expend-button")
            if expand_button:
                expand_button.click()  # 点击元素
                print("Clicked on expand button.")
            else:
                print("Expand button not found.")
        except Exception as e:
            print(f"Expand button not found or click failed: {e}")
    
        return {"title": title}  # 可以根据需要返回更多数据

        

    def get_multiple_product_details(self, urls):
        options = webdriver.ChromeOptions()
        options.debugger_address = f"localhost:{self.remote_debugging_port}"
        
        self.driver = webdriver.Chrome(options=options)
        product_details = []
        
        for url in urls:
            print(url)
            data = self.get_product_details(url)
            if data:
                product_details.append((data))
                print(data)
        
        self.driver.quit()
        return product_details
    
    def execute_detail(self, urls):
        print("start pro")
        self.start_chrome_with_debugging()
        self.get_multiple_product_details(urls)

if __name__ == '__main__':
    urls= ["https://detail.1688.com/offer/717125263963.html",
           "https://detail.1688.com/offer/741613702911.html",
           "https://detail.1688.com/offer/821154986517.html",
            "https://detail.1688.com/offer/729233690815.html",
            "https://detail.1688.com/offer/773959819091.html",
            "https://detail.1688.com/offer/673053584921.html"
           ]
    ProductScraper = ProductScraper()
    ProductScraper.execute_detail(urls)
    print('initial product class')

