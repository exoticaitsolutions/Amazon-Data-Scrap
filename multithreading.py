import csv
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import random
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# List of proxy IPs (Replace with your proxy list)
proxies = ["IP1:PORT", "IP2:PORT", "IP3:PORT", "IP4:PORT"]
# List of Amazon product links to be scraped
links = [
    "https://www.amazon.com/Valvoline-Hydraulic-Fluid-Gal/dp/B00AC7Q65E/ref=sr_1_1?dib=eyJ2IjoiMSJ9.lA5r2YT8byaxVMjFl57n4Q.rtZwMPNpEG-KzdYmAB4pkcGdOJehTNBbQcwajRfHDjM&dib_tag=se&keywords=%27074130007000&qid=1729227332&sr=8-1", 
    "https://www.amazon.com/Mersen-MERA6D4-5R-A6D4-1-CLASS-0-30A/dp/B002E80B8W/ref=sr_1_1?dib=eyJ2IjoiMSJ9.oT9y3V1MaORbcOYoqhN0g_OwJl3trOIKYov8plIK7NI.ltY9N7qXF1OMoW_wSxZr9FLz_Ox3Ki9pEyiMpHbG-Vs&dib_tag=se&keywords=782001991722&qid=1729227423&sr=8-1",
    "https://www.amazon.com/Cooper-Bussmann-FNQ-R-2-Class-Delay/dp/B000LETBX2/ref=sr_1_1?dib=eyJ2IjoiMSJ9.qTTddmhMz3slw27uvM-vmQ.K4QxcSVi2XHiAXJw8yasMw41ZjP2ZuCYcMazN4jyx4k&dib_tag=se&keywords=%27051712147064&qid=1729227482&sr=8-1",
    "https://www.amazon.com/Pferd-Needle-Diamond-Coarse-Length/dp/B002UUMRQ8/ref=sr_1_1?dib=eyJ2IjoiMSJ9.eDYrVAwwjGd-zCDnG8IIXw.x-xw3167BDGWgLLT-LfYqQPrePEbJHAjtjjy8HSSa1M&dib_tag=se&keywords=%27097758040129&qid=1729227550&sr=8-1",
    "https://www.amazon.com/Miniature-Lamp-194G-4-0W-PK10/dp/B07GTJZZ7N/ref=sr_1_1?dib=eyJ2IjoiMSJ9.ilDuPyxMyelkpkg6EwON1g.dvvDnAqKCfnQiiVPIUsxSGlOnOc4apucnfPWuENKw5w&dib_tag=se&keywords=190735569818&qid=1729227616&s=electronics&sr=1-1", 
    "https://www.amazon.com/puxyblue-316135401-Frigi-daire-316224200-EAP2361362/dp/B0C8MZT7RW/ref=sr_1_1_sspa?keywords=%27059733850031&qid=1729227683&s=electronics&sr=1-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9idGY&psc=1", 
    "https://www.amazon.com/Quantum-Storage-TC500GY-Tool-Caddy/dp/B002MRQQI4/ref=sr_1_1?dib=eyJ2IjoiMSJ9.Ccg5u7rujHx1UHQNd-pnvYG8UeA8T0GEOileTc_omrY.4Vu8uZeCuNLWUITcoZqz0TX4Qa52VDVqrUgVaY8CFYM&dib_tag=se&keywords=651588039519&qid=1729227805&sr=8-1&th=1", 
    "https://www.amazon.com/Osakesukar-Compatible-2003-2008-Silverado-Avalanche/dp/B0C3G562HW/ref=sr_1_1_sspa?keywords=20066773854&qid=1729227866&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9idGY&psc=1", 
    "https://www.amazon.com/532187292-532187281-532192870-195945-Husqvarna/dp/B0D149PYNP/ref=sr_1_1_sspa?keywords=00772313490&qid=1729227936&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9idGY&th=1",
    "https://www.amazon.com/Valvoline-Hydraulic-Fluid-Gal/dp/B00AC7Q65E/ref=sr_1_1?dib=eyJ2IjoiMSJ9.lA5r2YT8byaxVMjFl57n4Q.rtZwMPNpEG-KzdYmAB4pkcGdOJehTNBbQcwajRfHDjM&dib_tag=se&keywords=%27074130007000&qid=1729227332&sr=8-1"
]

# Function to chunk the links
def chunk_links(links, num_chunks):
    for i in range(0, len(links), num_chunks):
        yield links[i:i + num_chunks]

# Function to get a random proxy
def get_random_proxy():
    return random.choice(proxies)

# Function to get a random user-agent
ua = UserAgent()

def get_random_user_agent():
    return ua.random

# Selenium WebDriver setup with proxy and user-agent
def setup_selenium_driver(proxy, user_agent):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless if you don't need to see the browser
    chrome_options.add_argument(f"--proxy-server={proxy}")  # Add proxy
    chrome_options.add_argument(f"user-agent={user_agent}")  # Add random user-agent

    # Optional: Disable images to make scraping faster
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome()  # Adjust this path if you're using ChromeDriver
    return driver

# Scrape function that each thread will run
def scrape_amazon(links_chunk, thread_id):
    proxy = get_random_proxy()
    user_agent = get_random_user_agent()
    
    driver = setup_selenium_driver(proxy, user_agent)
    print(f"Thread {thread_id} - Using Proxy: {proxy} - User-Agent: {user_agent}")

    # Open a new CSV file for each thread
    start_time = time.time()
    csv_filename = f'amazon_product_titles_thread_{thread_id}.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['URL', 'Title'])

        for link in links_chunk:
            try:
                driver.get(link)
                time.sleep(8)
                try:    
                    get_title = driver.find_element(By.XPATH, '//*[@id="productTitle"]')
                    title = get_title.text
                    print(f"Thread {thread_id} - Product Title: {title}")
                    writer.writerow([link, title])
                except NoSuchElementException:
                    print(f"Thread {thread_id} - Title not found for {link}.")
            except Exception as e:
                print(f"Thread {thread_id} - Error on Request: {e}")
                break

    driver.quit()
    print(f"Thread {thread_id} completed")
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Thread {thread_id} completed in {total_time:.2f} seconds")
    print(f"Thread {thread_id} completed")

# Thread worker function
def worker(thread_id, links_chunk):
    scrape_amazon(links_chunk, thread_id)

# Main function to create and start multiple threads
def run_threads(num_threads):
    threads = []
    links_chunks = list(chunk_links(links, len(links) // num_threads))

    for i in range(num_threads):
        thread = threading.Thread(target=worker, args=(i, links_chunks[i]))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to finish
    for thread in threads:
        thread.join()

# Run the scraper with configurable threads
if __name__ == "__main__":
    NUM_THREADS = 4  # For example, 4 threads
    run_threads(NUM_THREADS)
