import tkinter as tk
from tkinter import scrolledtext, ttk
from scraper.search_scraper import SearchScraper  # 导入 SearchScraper 类
from scraper.product_scraper import ProductScraper  # 导入 ProductScraper 类

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("1688 Scraper")
        self.geometry("800x600")
        
        self.keyword_label = tk.Label(self, text="Enter Keyword:")
        self.keyword_label.pack(pady=10)
        
        self.keyword_entry = tk.Entry(self, width=50)
        self.keyword_entry.pack(pady=10)
        
        self.search_button = tk.Button(self, text="Search", command=self.start_search)
        self.search_button.pack(pady=10)
        
        self.price_button = tk.Button(self, text="获取价格参数", command=self.get_prices)
        self.price_button.pack(pady=10)
        
        # 显示获取到产品链接的文本
        self.result_text = scrolledtext.ScrolledText(self, width=70, height=15)
        self.result_text.pack(pady=10)
        
        # 创建一个表格来显示结果
        self.result_tree = ttk.Treeview(self, columns=("Title", "Price"), show="headings", height=15)
        self.result_tree.column("Title", width=500, anchor=tk.W)
        self.result_tree.column("Price", width=100, anchor=tk.CENTER)
        self.result_tree.heading("Title", text="Title")
        self.result_tree.heading("Price", text="Price")
        self.result_tree.pack(pady=10)
        
        self.links = []  # 用于存储搜索结果中的链接
        
    def start_search(self):
        keyword = self.keyword_entry.get()
        self.result_text.insert(tk.END, f"Searching for: {keyword}\n")
        
        # 调用爬虫模块
        scraper = SearchScraper()  # 创建 SearchScraper 类的实例
        self.links = scraper.execute_search(keyword)  # 使用实例调用 search_keyword 方法
        
        # 清空结果显示框
        self.result_text.delete(1.0, tk.END)
        
        if self.links:
            for link in self.links:
                self.result_text.insert(tk.END, f"{link}\n")
        else:
            self.result_text.insert(tk.END, "No results found.\n")

    def get_prices(self):
        if not self.links:
            self.result_text.insert(tk.END, "No links available. Please perform a search first.\n")
            return
        
        scraper = ProductScraper()
        product_details = scraper.get_multiple_product_details(self.links)
        
        # 清空表格中的旧数据
        for i in self.result_tree.get_children():
            self.result_tree.delete(i)
        
        # 将新的数据插入表格
        for title, price in product_details:
            self.result_tree.insert("", tk.END, values=(title, price))

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
