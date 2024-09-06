from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import csv
from seleniumbase import Driver
from time import sleep
from amazoncaptcha import AmazonCaptcha

options = Options()
options.add_argument("--disable-notifications")
options.add_argument("--start-maximized")
driver = Driver(uc=True, headless=False)

ids = ["'074130007000", "782001991722", "'051712147064", "'097758040129", "190735569818", "'059733850031", "190735975978", "715005432694", "651588039519", "20066773854", "0772313490"]
overall = []

def captcha_bypass():
    try:
        captcha_field = driver.find_element(By.ID, "captchacharacters")
        captcha_field.send_keys(solution)  # Use the solution variable
        button = driver.find_element(By.CLASS_NAME, "a-button-text")
        button.click()
        sleep(2)
        print(f"Captcha solution: {solution}")
        print("CAPTCHA bypassed.")
    except NoSuchElementException:
        print("No CAPTCHA found, proceeding with the search.")

try:
    driver.get("https://www.amazon.com/")
    captcha = AmazonCaptcha.fromdriver(driver)
    sleep(2)
    solution = captcha.solve()
    captcha_bypass()

    for product_id in ids:
        all_data = []
        attempts = 0
        while attempts < 3:
            print(f"\nAttempt {attempts + 1}")
            sleep(3)
            search_box = driver.find_element(By.ID, "twotabsearchtextbox")
            search_box.clear()
            search_box.send_keys(product_id)
            search_box.submit()
            sleep(2)

            try:
                product_cards = driver.find_elements(By.XPATH, '//div[contains(@class, "s-result-item s-asin")]')
            except:
                product_cards = []

            if product_cards:
                box_links = []
                elements = driver.find_elements(By.XPATH, '//a[@class = "a-link-normal s-no-outline"]')
                length = min(len(elements), 3)  # Limit to 3 products

                for element in elements[:length]:
                    box_links.append(element.get_attribute('href'))

                print(f"Found {length} products: {box_links}")
                product_data = [product_id]  # Start with the product ID

                for i, link in enumerate(box_links):
                    sleep(5)
                    driver.get(link)  # Navigate to each product page
                    try:
                        current_link = driver.current_url
                        try:
                            price_element = driver.find_element(By.CSS_SELECTOR, ".a-price.aok-align-center.reinventPricePriceToPayMargin.priceToPay")
                            price = price_element.text
                        except:
                            price = 'N/A'

                        try:
                            sold_by_element = driver.find_element(By.XPATH, '//*[@id="merchantInfoFeature_feature_div"]/div[2]/div/span')
                            sold_by = sold_by_element.text
                        except:
                            sold_by = 'N/A'

                        try:
                            asin_element = driver.find_element(By.XPATH, "//th[contains(text(), 'ASIN')]/following-sibling::td")
                            asin_value = asin_element.text
                        except:
                            asin_value = 'N/A'

                        try:
                            best_sellers_rank_element = driver.find_element(By.XPATH, "//th[contains(text(), 'Best Sellers Rank')]/following-sibling::td//span[1]")
                            best_sellers_rank = best_sellers_rank_element.text
                            rank_value = best_sellers_rank.split(" in ")[0]
                            rank_category = best_sellers_rank.split(" in ")[1].split(" (")[0]
                        except:
                            rank_value, rank_category = 'N/A', 'N/A'

                        data = [current_link, price, sold_by, rank_value, rank_category, asin_value]
                        product_data.extend(data)
                        print(f"Collected data for product {i+1}: {data}")
                        sleep(2)

                    except NoSuchElementException:
                        print(f"Error extracting data for ID {product_id}")
                        break
                overall.append(product_data)
                break  # Exit retry loop after successful data extraction
            else:
                print(f"No results found for {product_id}. Retrying with leading zeros.")
                product_id = f"0{product_id}"  # Add leading zero and retry
                attempts += 1

        if not product_data:
            # If no data was found after 3 attempts, append "N/A" for each column
            all_data = [product_id, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"]

finally:
    driver.quit()

print("OVERALL DATA:", overall)

# Write to CSV
csv_filename = "amazon_11products_data.csv"
csv_columns = ["product id", "Amazon Link1", "Buy Box Price1", "Buy Box Winner1", "BSR1", "Category1", "ASIN1", 
               "Amazon Link2", "Buy Box Price2", "Buy Box Winner2", "BSR2", "Category2", "ASIN2",
               "Amazon Link3", "Buy Box Price3", "Buy Box Winner3", "BSR3", "Category3", "ASIN3"]

with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(csv_columns)
    
    for row in overall:
        if len(row) < len(csv_columns):
            # Ensure each row has enough columns
            row.extend(["N/A"] * (len(csv_columns) - len(row)))
        writer.writerow(row)

print(f"Data has been written to {csv_filename}")
