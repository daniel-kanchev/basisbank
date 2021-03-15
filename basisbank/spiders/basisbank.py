import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from basisbank.items import Article


class BasisbankSpider(scrapy.Spider):
    name = 'basisbank'
    start_urls = ['https://basisbank.ge/en/news']

    def parse(self, response):
        articles = response.xpath('//td[@class="anlNoteSubject"]/a')
        for article in articles:
            link = article.xpath('./@href').get()
            title = article.xpath('./text()').get()
            yield response.follow(link, self.parse_article, cb_kwargs=dict(title=title))

        next_page = response.xpath('//td[@width="73%"]/div/div[@style="text-align:center;"]/a[last()]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, title):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        date = response.xpath('//div[@class="anlNoteDate"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//td[@width="73%"]/div//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[2:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
