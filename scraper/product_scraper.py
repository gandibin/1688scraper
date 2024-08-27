import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import subprocess
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
import os  
import getpass
from asyncio.tasks import wait


class ProductScraper:
    def __init__(self):
        self.chrome_path = self.get_chrome_path_by_user()
        self.user_data_dir = "C:/ChromeDevSession"
        self.remote_debugging_port = 9222
        self.driver = None
    
    def get_chrome_path_by_user(self):
        # 获取当前用户名
        username = getpass.getuser()
        # 根据用户名构造 Chrome 的路径
        chrome_base_path = r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe"
        chrome_path = chrome_base_path.format(username)

        # 检查路径是否存在
        if os.path.exists(chrome_path):
            return chrome_path
        else:
            raise FileNotFoundError(f"Chrome executable not found for user {username} at {chrome_path}")


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
        self.driver.execute_script(f"window.scrollBy(0, 400);")
    
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
                pass
        except:
            pass
        
            # 打印 SKU 详情
        self.print_sku_details()
    
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
            time.sleep(5)
        
        self.driver.quit()
        return product_details
    
    def execute_detail(self, urls):
        print("start pro")
        self.start_chrome_with_debugging()
        self.get_multiple_product_details(urls)
        
        
        
        
        
    def print_sku_details(self):
        company_element = self.driver.find_element(By.CSS_SELECTOR, "#hd_0_container_0 > div:nth-child(1) > div:nth-child(2) > div > div:nth-child(1) > div:nth-child(3) > div > div:nth-child(1) > span")
        company_name = company_element.text.strip()
        print(company_name)
        try:
            # 尝试查找 class="selector-table" 的 div
            sku_table = self.driver.find_element(By.CLASS_NAME, "selector-table")
            header_elements =  sku_table.find_elements(By.CSS_SELECTOR, "div.next-table-header-inner th")
            headers = [header.text for header in header_elements]
            # Extract table rows
            body_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.next-table-body table tbody tr.next-table-row")
            # 获取 class="summary-num" 的数值
            summary_num_element = self.driver.find_element(By.CLASS_NAME, "summary-num")
            summary_num_value = int(summary_num_element.text.strip())
            print(f"sku quantity is {summary_num_value}")
            for row in zip(body_elements,range(summary_num_value)):
                # Extract individual cell data
                row_dict = {}
                cells = row.find_elements(By.TAG_NAME, "td")
                i =0 
                for cell in cells:
                    row_dict[headers[i]] = cell.text
                    i = i+1
                
                print(f"{row_dict}")
                j = j+1
                if j>summary_num_value:
                    break
                    
            


        except Exception as e:
            print(f"try sku wraper")
            
            try:
                # 如果找不到 'selector-table'，再查找 class="pc-sku-wrapper" 的 div
                sku_wrapper = self.driver.find_element(By.CLASS_NAME, "pc-sku-wrapper")
                # 查找所有 class="sku-item-wrapper" 的 div，其中包含每个 SKU 的详细信息
                sku_items = sku_wrapper.find_elements(By.CLASS_NAME, "sku-item-wrapper")
                for sku_item in sku_items:
                    # 获取产品名称
                    name_element = sku_item.find_element(By.CLASS_NAME, "sku-item-name")
                    name = name_element.text.strip()
                    # 获取价格信息
                    price_element = sku_item.find_element(By.CLASS_NAME, "discountPrice-price")
                    price = price_element.text.strip()
                    print(f"Found SKU: {name}, Price: {price}")

            except Exception as e:
                print(f"'pc-sku-wrapper' not found")




if __name__ == '__main__':
    urls= ["https://detail.1688.com/offer/717125263963.html",
           "https://detail.1688.com/offer/741613702911.html",
           "https://detail.1688.com/offer/821154986517.html",
            "https://detail.1688.com/offer/729233690815.html",
            "https://detail.1688.com/offer/773959819091.html",
            "https://detail.1688.com/offer/673053584921.html"
           ]
    #urls = ["https://detail.1688.com/offer/821154986517.html"]
    ProductScraper = ProductScraper()
    ProductScraper.execute_detail(urls)
    print("all urls check,wait 20 second and then close browser")
    ProductScraper.stop_chrome_debugging()
