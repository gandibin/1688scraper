import time
from selenium import webdriver
from selenium.webdriver.common.by import By

class ProductScraper:
    def __init__(self):
        self.chrome_path = r"C:\Users\Xingwei-Tech\AppData\Local\Google\Chrome\Application\chrome.exe"
        self.user_data_dir = "C:/ChromeDevSession"
        self.remote_debugging_port = 9222
        self.driver = None

    def start_chrome_with_debugging(self):
        self.driver = webdriver.Chrome(
            options=self.get_chrome_options()
        )
    
    def get_chrome_options(self):
        options = webdriver.ChromeOptions()
        options.debugger_address = f"localhost:{self.remote_debugging_port}"
        return options

    def get_product_details(self, url):
        self.driver.get(url)
        try:
            title = self.driver.find_element(By.CSS_SELECTOR, "h1.d-title").text
            price = self.driver.find_element(By.CSS_SELECTOR, "span.price").text
            return title, price
        except Exception as e:
            print(f"Failed to get details from {url}: {e}")
            return None, None

    def get_multiple_product_details(self, urls):
        self.start_chrome_with_debugging()
        product_details = []
        
        for url in urls:
            title, price = self.get_product_details(url)
            if title and price:
                product_details.append((title, price))
                print(f"Title: {title}, Price: {price}")
        
        self.driver.quit()
        return product_details
