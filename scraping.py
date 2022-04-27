# Import Splinter and BeautifulSoup
from dataclasses import dataclass
from tkinter import BROWSE
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    # Set up Splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
   
    news_title, news_paragraph = mars_news(browser)
    hemisphere_image_urls = hemi_data(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemisphere_image": hemisphere_image_urls
    }
    
    #Stop webdriver and return data
    browser.quit()
    return data

# Visit the mars nasa news site
def mars_news(browser):
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    html = browser.html
    news_soup = soup(html, 'html.parser')

    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None,None
    
    return news_title, news_p
# ### Featured Images

# Visit URL
def featured_image(browser):
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None
    
    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url

def mars_facts():
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None
    
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)
    
    return df.to_html(classes="table table-striped")

def hemi_data(browser):
    url = 'https://marshemispheres.com/'
    browser.visit(url)
    hemisphere_image_urls = []
    
    for post in range(4): 
        scraped_information = {}
    
        browser.find_by_css('a.itemLink.product-item h3')[post].click()
    
        # Get Image URL
        image = browser.links.find_by_text('Sample')
        scraped_information["Image_url"] = image['href']
    
        # Get Hemisphere Title
        title = browser.find_by_css('h2').text
        scraped_information["title"] = title
    
    
        hemisphere_image_urls.append(scraped_information)
    
        browser.back()
    return hemisphere_image_urls

if __name__ == "__main__":
    #If running as script, print scraped data
    print(scrape_all())






