from scraper.search_scraper import SearchScraper


if __name__ == '__main__':
    SearchScraper = SearchScraper()
    keywords= ["网关主板" ]
    for keyword in keywords:
        SearchScraper.execute_search(keyword)