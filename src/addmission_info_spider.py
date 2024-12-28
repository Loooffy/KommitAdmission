# crawler/spiders/link_spider.py
import scrapy
from urllib.parse import urlparse
from typing import Set

class LinkSpider(scrapy.Spider):
    name = 'link_spider'
    
    def __init__(self, start_url=None, school_name=None, *args, **kwargs):
        super(LinkSpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_url] if start_url else ['https://example.com']
        self.allowed_domains = [urlparse(self.start_urls[0]).netloc]
        self.found_urls: Set[str] = set()

    def parse(self, response):
        # 將當前 URL 加入已找到的集合中
        self.found_urls.add(response.url)
        
        # 提取所有連結
        for href in response.css('a::attr(href)').getall():
            yield response.follow(
                href,
                callback=self.parse,
                errback=self.handle_error
            )
        
        # 輸出找到的 URL
        yield {
            'url': response.url
        }
    
    def handle_error(self, failure):
        # 處理請求錯誤
        self.logger.error(f'Request failed: {failure.request.url}')

    def closed(self, reason):
        # 爬蟲結束時輸出統計資訊
        self.logger.info(f'Spider closed: {reason}')
        self.logger.info(f'Total unique URLs found: {len(self.found_urls)}')

# crawler/settings.py
BOT_NAME = 'link_crawler'

SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'

# 爬蟲設定
ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 16
DOWNLOAD_DELAY = 1.0

# 避免記憶體用量過大
DEPTH_LIMIT = 3
CLOSESPIDER_PAGECOUNT = 1000  # 最多爬取 1000 頁

# 請求標頭
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

# 管道設定
ITEM_PIPELINES = {
    'crawler.pipelines.URLPipeline': 300,
}

# 輸出設定
FEEDS = {
    '../data/specific_file.json': {
        'format': 'json',
        'encoding': 'utf8',
        'indent': 2,
    }
}

# crawler/pipelines.py
class URLPipeline:
    def process_item(self, item, spider):
        return item

# crawler/items.py
import scrapy

class URLItem(scrapy.Item):
    url = scrapy.Field()

# run.py
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

def main():
    # 設定要爬取的網站
    start_url = input("請輸入想爬取的網站: ")
    school_name = input("請輸入學校名稱: ")
    
    # 建立爬蟲程序
    process = CrawlerProcess(get_project_settings())
    
    # 啟動爬蟲
    process.crawl('link_spider', start_url=start_url, school_name=school_name)
    process.start()

if __name__ == "__main__":
    main()