import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re

# Get your 2Captcha API key from the environment variable
API_KEY = os.getenv('2CAPTCHA_API_KEY')


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

    #try:
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
    lic_number_input.send_keys('008375')
    print('Entered license number')

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

    # save the html from the page to a file
    with open('page.html', 'w') as f:
        f.write(driver.page_source)

    # Step 7: Wait for the result table to load
    #wait.until(EC.presence_of_element_located((By.XPATH, '//table[@class="formListing"]//th[contains(text(),"License Number")]')))
    wait.until(EC.presence_of_element_located((By.XPATH, '//td[@class="labelCell"]//span[contains(text(),"License Number")]')))
    #print('Result page loaded')

    # Step 8: Parse the HTML with BeautifulSoup and find the "ADC ENDOSCOPY SPECIALISTS" link
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    rows = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'itemRow'))
    )

    adc_link = None
    for row in rows:
        if 'Ambulatory Surgical Center' in row.text:
            links = row.find_elements(By.TAG_NAME, 'a')
            for link in links:
                link_text = link.text.strip()
                if re.search(r'^ADC ENDOSCOPY SPECIALISTS$', link_text):
                    adc_link = link
                    break
        if adc_link:
            break

    if adc_link:
        # Click the link
        adc_link.click()
    else:
        print('Could not find the ADC ENDOSCOPY SPECIALISTS link')

    time.sleep(30)

    #detailsTXRAS.do?anchor=2b99ad3.0.0
except Exception as e:
    print("An error occurred:", str(e))
        # Don't close the browser so you can inspect it
