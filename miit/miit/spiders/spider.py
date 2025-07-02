import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from scrapy.selector import Selector
from miit.items import MiitItem
from time import sleep
from loguru import logger

logger.remove(0)
logger.add("miit.log")

class SpiderSpider(scrapy.Spider):
    name = "spider"
    allowed_domains = ["www.miit.gov.cn"]
    start_urls = ["https://www.miit.gov.cn/search/zcwjk.html?websiteid=110000000000000&pg=&p=&tpl=14&category=183&q="]

    def __init__(self):
        self.driver = webdriver.Edge()
        self.wait = WebDriverWait(self.driver, 20)

    def parse(self, response):
        self.driver.get(response.url)

        page = 1

        while True:
            try:
                self.wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='pagination']")))
                logger.info(f"Scraping page {page}...")
                page_source = self.driver.page_source
                sel = Selector(text=page_source)

                try:
                    for each in sel.xpath("//div[@class='jcse-result-box search-list']"):
                        item = MiitItem()
                        item['title'] = each.xpath(".//div[@class='search-list-t']/a/text()").get()
                        item['date_time'] = each.xpath(".//div[@class='search-list-b']/span[2]/text()").get()
                        content_url = each.xpath(".//div[@class='search-list-t']/a/@href").get()
                        if content_url:
                            yield scrapy.Request(url=response.urljoin(content_url), callback=self.parse_content, meta={'item': item})
                        else:
                            yield item
                except StaleElementReferenceException:
                    logger.warning("StaleElementReferenceException: Retrying to find the elements.")
                    continue
                except TimeoutException:
                    logger.error("TimeoutException: Elements not found.")
                    break

                try:
                    initial_first_item = self.driver.find_element(By.XPATH, "//div[@class='jcse-result-box search-list'][1]//div[@class='search-list-t']/a").text
                except StaleElementReferenceException:
                    logger.warning("StaleElementReferenceException: Retrying to find the initial first item.")
                    continue
                except TimeoutException:
                    logger.error("TimeoutException: First item not found.")
                    break

                try:
                    sleep(1)
                    next_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='pagination']//a[contains(text(), " + str(page + 1) + ")]")))
                    logger.info(f"Clicking next button: {next_button.text}")
                    next_button.click()
                    page += 1
                    logger.info(f"Waiting for the page {page} to load...")
                except StaleElementReferenceException:
                    logger.warning("StaleElementReferenceException: Retrying to find the next button.")
                    continue
                except TimeoutException:
                    logger.error("TimeoutException: Next button not found.")
                    break

                retry = 0
                while retry < 5:
                    try:
                        self.wait.until(lambda driver: driver.find_element(By.XPATH, "//div[@class='jcse-result-box search-list'][1]//div[@class='search-list-t']/a").text != initial_first_item)
                        break
                    except StaleElementReferenceException:
                        logger.warning("StaleElementReferenceException: Retrying to find the first item.")
                        retry += 1
                        sleep(1)
                        continue
                    except TimeoutException:
                        logger.error("TimeoutError: The first item did not change.")
                        retry += 1
                        sleep(1)
                        continue

                self.wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='pagination']")))
                logger.info(f"Page {page} loaded successfully.")

            except StaleElementReferenceException:
                logger.warning("StaleElementReferenceException: Retrying to find the pagination.")
                continue
            
            except TimeoutException as e:
                logger.error(f"TimeoutException: {str(e)}")
                break

            except Exception:
                logger.error("An unexpected error occurred.")
                break

        logger.info("No more pages to scrape. Closing the driver.")
        
        self.driver.quit()

    def parse_content(self, response):
        item = response.meta['item']
        content = response.xpath('//*[@id="con_con"]/p/text()').getall()
        item['content'] = ''.join(content).strip()
        yield item