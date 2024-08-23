import subprocess
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import urllib
from nt import link

class SearchScraper:
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

    def generate_search_url(self, keyword):
        base_url = "https://s.1688.com/selloffer/offer_search.htm"
        encoded_keyword = urllib.parse.quote(keyword, encoding='gb2312')
        search_url = f"{base_url}?keywords={encoded_keyword}&spm=a260k.home2024.searchbox.0"
        return search_url

    def scroll_to_bottom(self):
        scroll_increment = "document.body.scrollHeight * 0.1"
        total_scroll_time = 10  # 总滚动时间10秒
        interval = 1  # 每0.6秒滚动一次
        
        for _ in range(int(total_scroll_time / interval)):
            self.driver.execute_script(f"window.scrollBy(0, {scroll_increment});")
            time.sleep(interval)
        time.sleep(2)
        
        
    def get_urls(self,url):
        #打开新的页面
        self.driver.get(url)
        # 滚动到页面底部
        self.scroll_to_bottom()
        # 获取 class 为 "feeds-wrapper" 的 div 下所有的 <a> 标签
        feeds_wrapper = self.driver.find_element(By.CLASS_NAME, "feeds-wrapper")
        links = feeds_wrapper.find_elements(By.TAG_NAME, "a")
        
        # 获取以 https://detail.1688.com 开头的链接
        urls = [link.get_attribute("href") for link in links if link.get_attribute("href").startswith("https://detail.1688.com")]
        return urls

    def search_keyword(self, keyword):
        options = webdriver.ChromeOptions()
        options.debugger_address = f"localhost:{self.remote_debugging_port}"
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("https://www.1688.com")
        url = self.generate_search_url(keyword)
        self.driver.get(url)
        
        print(f"已导航至: {url}")
        
        # 滚动到页面底部
        self.scroll_to_bottom()

        # 获取 class 为 "feeds-wrapper" 的 div 下所有的 <a> 标签
        feeds_wrapper = self.driver.find_element(By.CLASS_NAME, "feeds-wrapper")
        links = feeds_wrapper.find_elements(By.TAG_NAME, "a")
        
        # 获取以 https://detail.1688.com 开头的链接
        urls = [link.get_attribute("href") for link in links if link.get_attribute("href").startswith("https://detail.1688.com")]
        
        all_urls = []
        all_urls.extend(urls)
        
        # 获取总页数
        total_pages_element = self.driver.find_element(By.CLASS_NAME, "fui-paging-num")
        total_pages = int(total_pages_element.text)
        print(f"Total pages found: {total_pages}")
        # 最多抓取10页
        max_pages = min(total_pages, 10)
        i = 2
        for page in range(1, max_pages):
            time.sleep(5)
            new_links = f"{url}&beginPage={i}"
            print(f"new link is:{new_links}")
            urls =self.get_urls(new_links)
            all_urls.extend(urls)
            i =i +1
            
        return all_urls
            
        

    def execute_search(self, keyword):
        self.start_chrome_with_debugging()
        urls = self.search_keyword(keyword)
        
        file_name = f"{keyword}.txt"
        with open(file_name, "w", encoding="utf-8") as file:
            for url in urls:
                print(url)
                file.write(url + "\n")
        print(f"URLs have been saved to {file_name}")
        self.stop_chrome_debugging()
            
