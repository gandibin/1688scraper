import time
import os
import getpass
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
import tkinter as tk
from tkinter import messagebox
from urllib.parse import urlparse

class ProductScraper:
    def __init__(self):
        self.chrome_path = self.get_chrome_path_by_user()
        self.user_data_dir = "C:/ChromeDevSession"
        self.remote_debugging_port = 9222
        self.driver = None
    
    def get_chrome_path_by_user(self):
        username = getpass.getuser()
        chrome_base_path = r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe"
        chrome_path = chrome_base_path.format(username)
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
        start_time = time.time()
        max_wait_time = 4
        while self.chrome_process.poll() is None:
            if time.time() - start_time > max_wait_time:
                break
            time.sleep(0.5)
        

    def stop_chrome_debugging(self):
        if self.chrome_process is not None:
            try:
                self.chrome_process.terminate()
                self.chrome_process.wait()
                print("Chrome 调试进程已终止")
            except Exception as e:
                print(f"终止 Chrome 调试进程失败: {e}")
                

    def scroll_to_bottom(self):
        scroll_increment = "document.body.scrollHeight * 0.1"
        total_scroll_time = 10
        interval = 1
        for _ in range(int(total_scroll_time / interval)):
            self.driver.execute_script(f"window.scrollBy(0, {scroll_increment});")
            time.sleep(interval)
        time.sleep(2)
        

    def wait_for_page_load_complete(self, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
        except TimeoutException:
            print("Page load timed out after waiting.")
                    

    def get_multiple_product_details(self, urls):
        options = webdriver.ChromeOptions()
        options.debugger_address = f"localhost:{self.remote_debugging_port}"
        self.driver = webdriver.Chrome(options=options)
        product_details = []
        
        for url in urls:
            print(url)
            data = self.get_product_details(url)
            if data:
                product_details.append(data)
                print(data)
            time.sleep(5)
        self.driver.quit()
        return product_details

    #获取店铺的地址
    def get_shop_link(self):
        # 使用 Selenium 查找所有 class="primary-row-link" 的 a 标签
        links = self.driver.find_elements(By.CLASS_NAME, "primary-row-link") 
        # 使用集合来存储并去重域名
        domains = set()
        # 提取链接并获取域名部分
        for link in links:
            href = link.get_attribute('href')
            if href:
                parsed_url = urlparse(href)
                domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
                domains.add(domain)
        return domains  # 你可以根据需要返回或处理这个集合
            
    
    def get_product_details(self, url):
        self.driver.get(url)
        time.sleep(3)
        self.wait_for_page_load_complete()
        self.driver.execute_script("window.scrollBy(0, 400);")
        #产品标题
        title = self.driver.title
        company_element = self.driver.find_element(By.CSS_SELECTOR, "#hd_0_container_0 > div:nth-child(1) > div:nth-child(2) > div > div:nth-child(1) > div:nth-child(3) > div > div:nth-child(1) > span")
        #公司名称
        company_name = company_element.text.strip()
        #store_links
        shop_link = self.get_shop_link()
        
        #产品的SKU价格信息
        sku_data =self.sku_details(url)
        
        attributes = self.get_product_attributes()
        
        print(f"title: ---- {title}")
        print(f"company name ---- {company_name}")
        print(f"shop_link ---- {shop_link}")
        print(f"sku_data ----{sku_data}")
        print(f"attributes ----{attributes}")
        print("----------------------------------")
        



    def execute_detail(self, urls):
        self.start_chrome_with_debugging()
        self.get_multiple_product_details(urls)
    
    
    #获取产品的SKU价格
    def sku_details(self, url): 
        sku_data = []
        try:
            # 尝试查找 selector-table
            sku_table = self.driver.find_elements(By.CLASS_NAME, "selector-table")
        except Exception as e:
            sku_table = []
        try:
            # 尝试查找 pc-sku-wrapper
            sku_wrapper = self.driver.find_elements(By.CLASS_NAME, "pc-sku-wrapper")
        except Exception as e:
            sku_wrapper = []     
        # 如果找到了 selector-table，则获取 SKU 信息
        if sku_table:
            sku_table = sku_table[0]  # 因为 find_elements 返回列表，这里取第一个元素
            header_elements = sku_table.find_elements(By.CSS_SELECTOR, "div.next-table-header-inner th")
            headers = [header.text for header in header_elements]
            body_elements = sku_table.find_elements(By.CSS_SELECTOR, "div.next-table-body table tbody tr.next-table-row")
            summary_num_element = self.driver.find_element(By.CLASS_NAME, "summary-num")
            summary_num_value = int(summary_num_element.text.strip())
            for row in zip(body_elements, range(summary_num_value)):
                row_dict = {headers[i]: cell.text for i, cell in enumerate(row[0].find_elements(By.TAG_NAME, "td"))}
                sku_data.append(row_dict)
        # 如果没有找到 selector-table，但找到了 pc-sku-wrapper，则获取 SKU 信息
        elif sku_wrapper:
            sku_wrapper = sku_wrapper[0]  # 取第一个元素
            # 尝试展开隐藏的 SKU 项
            expand_button = self.driver.find_elements(By.CLASS_NAME, "sku-wrapper-expend-button")
            if expand_button:
                try:
                    expand_button[0].click()
                except Exception:
                    pass
            sku_items = sku_wrapper.find_elements(By.CLASS_NAME, "sku-item-wrapper")
            for sku_item in sku_items:
                name = sku_item.find_element(By.CLASS_NAME, "sku-item-name").text.strip()
                price = sku_item.find_element(By.CLASS_NAME, "discountPrice-price").text.strip()
                row_dict = {"product_name": name, "price": price}
                sku_data.append(row_dict)
        # 如果两种方法都未找到，进行错误处理
        else:
            print("Both methods failed. Please check if verification is required.")
            self.alert_and_wait()
            self.get_product_details(url)
        return sku_data


    def alert_and_wait(self):        
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showinfo("操作提示", "无法获取SKU信息，请检查是否有验证码或其他问题需要手动解决后点击确定重新爬取。")
        root.destroy()

    
    def get_product_attributes(self):
        # 初始化一个空字典来存储属性
        product_attributes = {}
        try:
            # 尝试查找 offer-attr-switch 元素并点击展开
            switch_elements = self.driver.find_elements(By.CLASS_NAME, "offer-attr-switch")
            if switch_elements:
                for switch in switch_elements:
                    try:
                        switch.click()
                    except:
                        print("Failed to click on an offer-attr-switch element, skipping to the next one.")
                        continue
        except:
            print("No offer-attr-switch elements found.")
        # 查找包含所有属性的父容器
        try:
            attr_lists = self.driver.find_elements(By.CLASS_NAME, "offer-attr")
            # 查找所有的属性项
            for attr_list in attr_lists:
                attr_items = attr_list.find_elements(By.CLASS_NAME, "offer-attr-item")
                # 遍历每个属性项并提取属性名和值
                for item in attr_items:
                    name_element = item.find_element(By.CLASS_NAME, "offer-attr-item-name")
                    value_element = item.find_element(By.CLASS_NAME, "offer-attr-item-value")
                    # 获取属性名和值的文本
                    attr_name = name_element.text.strip()
                    attr_value = value_element.text.strip()
                    # 将属性名和值存入字典
                    product_attributes[attr_name] = attr_value
        except:
            print("offer-attr-wrapper or offer-attr-item elements found.")
        return product_attributes

# 使用示例：
# from selenium import webdriver
# driver = webdriver.Chrome()
# your_instance = YourClassName(driver)
# attributes = your_instance.get_product_attributes()
# print(attributes)




if __name__ == '__main__':
    urls = [
        "https://detail.1688.com/offer/717125263963.html",
        "https://detail.1688.com/offer/741613702911.html",
        "https://detail.1688.com/offer/821154986517.html",
        "https://detail.1688.com/offer/729233690815.html",
        "https://detail.1688.com/offer/773959819091.html",
        "https://detail.1688.com/offer/673053584921.html"
    ]
    scraper = ProductScraper()
    scraper.execute_detail(urls)
    print("All URLs checked, waiting 20 seconds before closing the browser...")
    time.sleep(20)
    scraper.stop_chrome_debugging()
