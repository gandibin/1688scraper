import tkinter as tk
from tkinter import scrolledtext
from scraper.search_scraper import search_keyword

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("1688 Scraper")
        self.geometry("600x400")
        
        self.keyword_label = tk.Label(self, text="Enter Keyword:")
        self.keyword_label.pack(pady=10)
        
        self.keyword_entry = tk.Entry(self, width=50)
        self.keyword_entry.pack(pady=10)
        
        self.search_button = tk.Button(self, text="Search", command=self.start_search)
        self.search_button.pack(pady=10)
        
        self.result_text = scrolledtext.ScrolledText(self, width=70, height=15)
        self.result_text.pack(pady=10)
        
    def start_search(self):
        keyword = self.keyword_entry.get()
        self.result_text.insert(tk.END, f"Searching for: {keyword}\n")
        
        # 调用爬虫模块
        links = search_keyword(keyword)
        for link in links:
            self.result_text.insert(tk.END, f"{link}\n")

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
