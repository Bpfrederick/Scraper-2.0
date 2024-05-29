import os
import time
import requests
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re

# Load the Excel file
file_path = r"C:\Users\bfrederick\OneDrive - Heartland Medical Sales and Service\Heartland\ASCSCRAP\TXASCS.xlsx"
df = pd.read_excel(file_path, dtype=str)

# Get your 2Captcha API key from the environment variable
API_KEY = 'YOUR 2CAPTCHA API'

try:
    # Ensure the API key is not None
    print(API_KEY)
    if API_KEY is None:
        raise ValueError("Please set the 2CAPTCHA_API_KEY environment variable")

    # Constant site key for reCAPTCHA
    SITE_KEY = '6LdpIE4UAAAAAIYpCXPFjq8xqa9a5v9O7f2sprgJ'
    PAGE_URL = 'https://vo.ras.dshs.state.tx.us/datamart/searchByLicNumberTXRAS.do'

    # Chrome options for running headed
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--start-maximized')

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 30)

    def solve_recaptcha(site_key, page_url):
        # Initiate captcha request
        form_data = {
            'method': 'userrecaptcha',
            'googlekey': site_key,
            'key': API_KEY,
            'pageurl': page_url,
            'json': 1
        }
        response = requests.post('http://2captcha.com/in.php', data=form_data)
        request_id = response.json().get('request')

        # Poll for result
        result_url = f"http://2captcha.com/res.php?key={API_KEY}&action=get&id={request_id}&json=1"
        while True:
            result_response = requests.get(result_url)
            result = result_response.json()
            if result.get('status') == 1:
                return result.get('request')
            time.sleep(5)

    # Format license numbers to ensure leading zeros
    lic_numbers = [num.zfill(6) for num in df['LICENSE NUMBER']]

    # Start from the specific row
    start_index = 553

    for index, lic_number in enumerate(lic_numbers[start_index:], start=start_index):
        retry_count = 0
        while retry_count < 3:
            try:
                print(f'Processing license number: {lic_number} (Row {index + 1})')
                
                # Step 1: Navigate to the login page
                driver.get('https://vo.ras.dshs.state.tx.us/datamart/login.do')
                print('Navigated to login page')

                # Step 2: Navigate to the licensing search page
                driver.get('https://vo.ras.dshs.state.tx.us/datamart/selSearchTypeTXRAS.do?from=loginPage')
                print('Navigated to licensing search page')

                # Step 3: Choose "Search by License Number"
                driver.get(PAGE_URL)
                print('Navigated to "Search by License Number" page')

                # Step 4: Input the license number
                lic_number_input = wait.until(EC.presence_of_element_located((By.ID, 'licNumber')))
                lic_number_input.send_keys(str(lic_number))
                print(f'Entered license number: {lic_number}')

                # Step 5: Solve the reCAPTCHA using 2Captcha
                recaptcha_response = solve_recaptcha(SITE_KEY, PAGE_URL)

                # Set the recaptcha response in the element
                driver.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML="{recaptcha_response}";')
                print('reCAPTCHA solved')

                # Wait for the recaptcha iframe to disappear
                time.sleep(2)  # Wait for a short time to ensure the recaptcha is processed

                # Step 6: Click the submit button and wait for navigation
                submit_button = driver.find_element(By.XPATH, '//input[@name="search" and @value="Search"]')
                driver.execute_script("arguments[0].click();", submit_button)
                print('Clicked the submit button')

                time.sleep(2)

                # Wait for the result table to load
                wait.until(EC.presence_of_element_located((By.XPATH, '//td[@class="labelCell"]//span[contains(text(),"License Number")]')))

                # Step 7: Parse the HTML with BeautifulSoup and find the link
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                rows = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//tr[contains(@class, 'itemRow') or contains(@class, 'itemRowAlt')]"))
                )

                asc_row = None
                for row in rows:
                    if 'Ambulatory Surgical Center' in row.text:
                        asc_row = row
                        break

                if asc_row:
                    link = asc_row.find_element(By.TAG_NAME, 'a')
                    if link:
                        link.click()
                        print('Navigated to the next page')
                    else:
                        print('No link found in the "Ambulatory Surgical Center" row')
                else:
                    print('No row found with "Ambulatory Surgical Center"')

                time.sleep(30)
                
                # Step 9: Parse the page to find the email address
                email_pattern = r'<([a-zA-Z][a-zA-Z0-9]*)\b[^>]*>([^<]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})<\/\1>'
                email_match = re.search(email_pattern, driver.page_source)
                
                if email_match:
                    email = email_match.group(2)
                    print(f"Found email address: {email}")
                    df.at[index, 'Email'] = email
                else:
                    print("No email address found in the HTML.")
                    df.at[index, 'Email'] = 'Not Found'

                # Save the updated DataFrame back to the Excel file after each email is found
                df.to_excel(file_path, index=False)
                print('Updated Excel file saved.')

                # Wait for the email to be processed
                time.sleep(2)  # Wait for a short time to ensure the email is processed

                # Step 10: Click the new criteria button and wait for navigation
                new_criteria = driver.find_element(By.XPATH, '//input[@name="newcriteria" and @value="New Search Criteria"]')
                driver.execute_script("arguments[0].click();", new_criteria)
                print('Clicked the New Criteria button')

                time.sleep(2)

                # Step 11: Click the clear button and wait for navigation
                clear = driver.find_element(By.XPATH, '//input[@name="clear" and @value="Clear"]')
                driver.execute_script("arguments[0].click();", clear)
                print('Clicked the Clear button')

                time.sleep(2)

                break

            except WebDriverException as e:
                retry_count += 1
                print(f"An error occurred: {e}. Retrying {retry_count}/3...")
                time.sleep(5)  # Wait before retrying

    # Save the updated DataFrame back to the Excel file one last time after all iterations
    df.to_excel(file_path, index=False)
    print('Final updated Excel file saved.')

except Exception as e:
    print("An error occurred:", str(e))
    # Don't close the browser so you can inspect it

finally:
    driver.quit()
