from scraper.search_scraper import SearchScraper



if __name__ == '__main__':
    SearchScraper = SearchScraper()
    keywords= ["路由器开发板" ,"软路由开发板","防火墙开发板","arm架构开发板","安卓开发板","linux开发板","开源系统开发板"]
    for keyword in keywords:
        SearchScraper.execute_search(keyword)