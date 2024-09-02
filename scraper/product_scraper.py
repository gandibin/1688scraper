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
import pandas as pd
from openpyxl import load_workbook
import sqlite3

class ProductScraper:
    def __init__(self):
        self.driver = None
        self.chrome_process =None
    

        

    def start_chrome_with_debugging(self):
        # 获取当前用户的用户名并构建Chrome的路径
        username = getpass.getuser()
        chrome_base_path = r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe"
        chrome_path = chrome_base_path.format(username)
    
        # 检查Chrome可执行文件是否存在
        if not os.path.exists(chrome_path):
            raise FileNotFoundError(f"未找到用户 {username} 的Chrome可执行文件，路径为 {chrome_path}")
        
        # 定义用户数据目录和远程调试端口
        user_data_dir = "C:/ChromeDevSession"
        remote_debugging_port = 9222
        
        # 启动带有远程调试功能的Chrome
        self.chrome_process = subprocess.Popen([
            chrome_path,
            f'--remote-debugging-port={remote_debugging_port}',
            f'--user-data-dir={user_data_dir}'
        ])
        
        # 给Chrome一些时间来启动
        start_time = time.time()
        max_wait_time = 4
        while self.chrome_process.poll() is None:
            if time.time() - start_time > max_wait_time:
                break
            time.sleep(0.5)
        
        # 设置Selenium连接到正在运行的调试模式下的Chrome实例
        options = webdriver.ChromeOptions()
        options.debugger_address = f"localhost:{remote_debugging_port}"
        self.driver = webdriver.Chrome(options=options)
        

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
        return str(domains)  # 你可以根据需要返回或处理这个集合
            
    
    def get_product_details(self,cursor, url):
        retry = 0
        while True:  # 循环直到成功获取产品信息
            try:
                self.driver.get(url)
                time.sleep(3)
                self.wait_for_page_load_complete()
                self.driver.execute_script("window.scrollBy(0, 400);")

                # 产品标题
                title = str(self.driver.title)
                company_element = self.driver.find_element(By.CSS_SELECTOR, "#hd_0_container_0 > div:nth-child(1) > div:nth-child(2) > div > div:nth-child(1) > div:nth-child(3) > div > div:nth-child(1) > span")
                # 公司名称
                company_name = str(company_element.text.strip())
                # store_links
                shop_link = self.get_shop_link()

                # 产品的SKU价格信息
                sku_data = self.sku_details(url)

                attributes = self.get_product_attributes()
                print(f"title: ---- {title}")
                print(f"company_name ---- {company_name}")
                print(f"shop_link ---- {shop_link}")
                print(f"sku_data ----{sku_data}")
                print(f"attributes ----{attributes}")
                print("----------------------------------")

                update_query = f"""
                UPDATE switch
                SET 
                    title = ?,
                    company_name = ?,
                    shop_link = ?,
                    sku_data = ?,
                    attributes = ?,
                    check_status = 1
                WHERE product_link = ?;
                """
                
                # 执行更新操作
                cursor.execute(update_query, (title,company_name,shop_link,sku_data,attributes,url))
                

                break  # 成功获取信息后跳出循环

            except Exception as e:
                print(f"Error encountered: {e}")
                
                # 在异常处理块中展开提示逻辑
                root = tk.Tk()
                root.title("操作提示")  # 设置窗口标题
                
                # 创建一个标签，提示用户手动操作
                label = tk.Label(root, text="检测到验证码，请手动解决问题后点击确定继续。")
                label.pack(padx=20, pady=20)
                
                # 标记用户的选择
                user_choice = tk.StringVar(value="repeat")  # 初始值为 "repeat"
            
                def on_repeat():
                    user_choice.set("repeat")
                    root.quit()
            
                def on_skip():
                    user_choice.set("skip")
                    root.quit()
            
                # 创建 "重复" 按钮
                repeat_button = tk.Button(root, text="重复", command=on_repeat)
                repeat_button.pack(side="left", padx=10, pady=10)
            
                # 创建 "跳过" 按钮
                skip_button = tk.Button(root, text="跳过", command=on_skip)
                skip_button.pack(side="right", padx=10, pady=10)
            
                # 进入事件循环，等待用户点击“重复”或“跳过”
                root.mainloop()
            
                # 根据用户选择执行不同的操作
                if user_choice.get() == "repeat":
                    # 当用户点击按钮后，销毁窗口
                    root.destroy()
                else:
                    # 当用户点击按钮后，销毁窗口
                    root.destroy()
                    update_query = f"""
                    UPDATE switch
                    SET 
                        check_status = 2
                    WHERE product_link = ?;
                    """
                    
                    # 执行更新操作
                    cursor.execute(update_query, (url,))
                    break  # 用户选择跳过，跳出循环
            

                            

    
    #获取产品的SKU价格
    def sku_details(self, url): 
        sku_data = []
        
        try:
            summary_num_element = self.driver.find_element(By.CLASS_NAME, "summary-num")
            summary_num_value = int(summary_num_element.text.strip())
        except Exception as e:
            summary_num_value = 0
        try:
            # 尝试查找 pc-sku-wrapper
            sku_wrapper = self.driver.find_elements(By.CLASS_NAME, "pc-sku-wrapper")
        except Exception as e:
            sku_wrapper = [] 
            
        try:
            price_text = self.driver.find_elements(By.CLASS_NAME, "price-text") 
        except:
            price_text =[]
        # 如果找到了 selector-table，则获取 SKU 信息
        if summary_num_value>0:
            print('类型1')
            sku_table = self.driver.find_elements(By.CLASS_NAME, "selector-table")
            sku_table = sku_table[0]  # 因为 find_elements 返回列表，这里取第一个元素
            header_elements = sku_table.find_elements(By.CSS_SELECTOR, "div.next-table-header-inner th")
            headers = [header.text for header in header_elements]
            body_elements = sku_table.find_elements(By.CSS_SELECTOR, "div.next-table-body table tbody tr.next-table-row")

            for row in zip(body_elements, range(summary_num_value)):
                row_dict = {headers[i]: cell.text for i, cell in enumerate(row[0].find_elements(By.TAG_NAME, "td"))}
                sku_data.append(row_dict)
        # 如果没有找到 selector-table，但找到了 pc-sku-wrapper，则获取 SKU 信息
        elif sku_wrapper:
            print('类型2')
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
        #看看有没有价格:
        elif price_text:
            print('类型3')
            price = price_text[0].text.strip()
            name = str(self.driver.title)
            row_dict = {"product_name": name, "price": price}
            sku_data.append(row_dict)
        
        # 如果两种方法都未找到，进行错误处理
        else:
            print("all methods failed. Please check if verification is required.")


        return str(sku_data)

     

    
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
        return str(product_attributes)




if __name__ == '__main__':
    current_dir = os.path.dirname(__file__)
    root_dir = os.path.dirname(current_dir)
    db_path = os.path.join(root_dir, "switch.db")  # Database file path
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # 执行查询，提取 check = 0 的所有 url
    cursor.execute("SELECT product_link FROM switch WHERE check_status = 0;")
    urls = cursor.fetchall()    
    
    scraper = ProductScraper()
    scraper.start_chrome_with_debugging()
    for url in urls:
        print(url[0])
        scraper.get_product_details(cursor,url[0])
        conn.commit()
    print("All URLs checked, waiting 10 seconds before closing the browser...")
    time.sleep(10)
    scraper.stop_chrome_debugging()
    conn.close()
    
