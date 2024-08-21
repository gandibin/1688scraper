import subprocess
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import urllib

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
        # 计算每次滚动的高度（10%）
        scroll_increment = "document.body.scrollHeight * 0.08"
        total_scroll_time = 7.2  # 总滚动时间5秒
        interval = 0.6  # 每0.5秒滚动一次
        
        for _ in range(int(total_scroll_time / interval)):
            self.driver.execute_script(f"window.scrollBy(0, {scroll_increment});")
            time.sleep(interval)
        time.sleep(2)

    def search_keyword(self, keyword):
        options = webdriver.ChromeOptions()
        options.debugger_address = f"localhost:{self.remote_debugging_port}"
        
        self.driver = webdriver.Chrome(options=options)
        
        try:
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

            print(f"找到的链接数量: {len(urls)}")
            for url in urls:
                print(url)

            return urls

        except Exception as e:
            print(f"搜索加载失败: {e}")
        finally:
            self.driver.quit()

    def execute_search(self, keyword):
        self.start_chrome_with_debugging()
        self.search_keyword(keyword)
        #self.stop_chrome_debugging()  # 自动停止调试进程

if __name__ == "__main__":
    scraper = SearchScraper()
    scraper.execute_search("交换机")
