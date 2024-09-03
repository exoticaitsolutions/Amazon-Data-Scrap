import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import csv, os
from seleniumbase import Driver
from time import sleep
import pytesseract
import numpy as np
import cv2

# Set up Chrome options
options = Options()
options.add_argument("--disable-notifications")
options.add_argument("--start-maximized")

# Set up the driver with undetected_chromedriver
driver = Driver(uc=True, headless=False)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# ids = ['074130007000', "'051712147064", "'097758040129", '190735569818', '651588039519', '20066773854', '0772313490']
ids = ["'051712147064", '190735569818','074130007000', "'097758040129", '651588039519', '0772313490', "'059733850031", "190735975978", "715005432694", '20066773854']
results = []

all_data = []
try:
    # Navigate to a website "'051712147064", '190735569818',
    driver.get("https://www.amazon.com/")
    sleep(25)
    
    while True:
        try:
            # Check if the CAPTCHA image is present
            image_element = driver.find_element(By.XPATH, '//div[@class = "a-row a-text-center"]/img')
            image = image_element.screenshot_as_png
            nparr = np.frombuffer(image, np.uint8)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            text = pytesseract.image_to_string(img_np)
            
            print("Extracted Text:", text)
            print("The text is:", text)
            sleep(2)
            
            input_element = driver.find_element(By.XPATH, '//*[@id="captchacharacters"]')
            input_element.send_keys(text)
            print("Text filled")
            sleep(5)
        except NoSuchElementException:
            # CAPTCHA is no longer present, break the loop
            print("CAPTCHA is not present, proceeding with the search.")
            break
    
    # Proceed with product search after CAPTCHA handling
    for product_id in ids:
        found_product = False
        attempts = 0

        while not found_product and attempts < 3:
            # Find and interact with search box
            search_box = driver.find_element(By.ID, "twotabsearchtextbox")
            search_box.clear()
            search_box.send_keys(product_id)
            search_box.submit()
            sleep(2)

            # Check if the desired search result is present
            if driver.find_elements(By.CSS_SELECTOR, ".a-section.aok-relative.s-image-square-aspect"):
                total_boxes =  driver.find_elements(By.CSS_SELECTOR, ".a-section.aok-relative.s-image-square-aspect")
                print(" total boxes : ", len(total_boxes))
                search_url_link = driver.current_url
                if(len(total_boxes) < 4):
                    length = len(total_boxes)
                else:
                    length = 3
                for i in range(1,length+1):
                    card =  driver.find_element(By.XPATH, f'//*[@data-image-index = "{i}"]').click()
                    # Initialize variables for each ID
                    current_link = "N/A"
                    price = "N/A"
                    sold_by = "N/A"
                    rank_value = "N/A"
                    rank_category = "N/A"
                    asin_value = "N/A"
                    da = []

                    # Extract data
                    try:
                        print("----------------------------------------"*8)
                        current_link = driver.current_url
                        print("current_link : ", current_link)
                        da.append(current_link)
                        price_element = driver.find_element(By.CSS_SELECTOR, ".a-price.aok-align-center.reinventPricePriceToPayMargin.priceToPay")
                        price = price_element.text
                        print("price_element : ", price)
                        da.append(price)
                        sold_by_element = driver.find_element(By.XPATH, '//*[@id="merchantInfoFeature_feature_div"]/div[2]')
                        sold_by = sold_by_element.text
                        print("sold_by : ", sold_by)
                        da.append(sold_by)
                        driver.execute_script("window.scrollBy(0, -document.body.scrollHeight * 0.8);")
                        sleep(5)
                        asin_element = driver.find_element(By.XPATH, "//th[contains(text(), 'ASIN')]/following-sibling::td")
                        asin_value = asin_element.text
                        print("asin_value : ", asin_value)
                        da.append(asin_value)
                        best_sellers_rank_element = driver.find_element(By.XPATH, "//th[contains(text(), 'Best Sellers Rank')]/following-sibling::td//span[1]")
                        best_sellers_rank = best_sellers_rank_element.text
                        print("best_sellers_rank : ", best_sellers_rank)
                        da.append(best_sellers_rank)
                        rank_value = best_sellers_rank.split(" in ")[0] if " in " in best_sellers_rank else best_sellers_rank
                        rank_category = best_sellers_rank.split(" in ")[1].split(" (")[0] if " in " in best_sellers_rank else "N/A"
                        da.append(rank_category)
                        print("----------------------------------------"*8)
                        if (i == length):
                            driver.get("https://www.amazon.com/")
                            sleep(5)
                        else:
                            driver.get(search_url_link)
                        found_product = True

                    except NoSuchElementException as e:
                        print(f"Error extracting data for ID {product_id}: {e}")
                        break
                attempts = 3
                all_data.append(da)

            elif driver.find_elements(By.CSS_SELECTOR, ".a-section.a-spacing-none"):
                print(f"Product ID {product_id} not found or has no results. Retrying with leading zeros.")
                attempts += 1
                product_id = f"0{product_id}"  # Prepend a zero to the ID for the next attempt
                sleep(2)
            else:
                print(f"Search result for ID {product_id} not found after {attempts} attempts.")
                break

        if not found_product:
            results.append([product_id, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"])
        else:
            # Append data for the current ID
            results.append([
                product_id,     # UPC Code
                current_link,   # Amazon Link
                price,          # Buy Box Price
                sold_by,        # Buy Box Winner
                rank_value,     # BSR
                rank_category,  # Category
                asin_value      # ASIN
            ])

finally:
    # Ensure the browser is closed properly
    try:
        driver.quit()
    except Exception as e:
        print(f"Error closing the browser: {e}")

# Write all data to CSV
csv_filename = "amazon_products_data.csv"

# Define CSV columns
csv_columns = ["UPC Code", "Amazon Link1", "Buy Box Price1", "Buy Box Winner1", "BSR1", "Category1", "ASIN1", "Amazon Link2", "Buy Box Price2", "Buy Box Winner2", "BSR2", "Category2", "ASIN2",
               "Amazon Link3", "Buy Box Price3", "Buy Box Winner3", "BSR3", "Category3", "ASIN3"]

# Writing to the CSV file
with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(csv_columns)  # Write the header
    writer.writerows(results)     # Write all rows of data

print(f"Data has been written to {csv_filename}")
