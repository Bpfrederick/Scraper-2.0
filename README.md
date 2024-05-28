# README

## Overview
This Python script automates the process of retrieving email addresses from the Texas Department of State Health Services licensing search website. The script reads license numbers from an Excel file, performs searches on the website, solves reCAPTCHAs using 2Captcha, and updates the Excel file with the found email addresses.

## Prerequisites
- Python 3.x
- Required Python libraries:
  - `os`
  - `time`
  - `requests`
  - `pandas`
  - `selenium`
  - `beautifulsoup4`
  - `re`
- Google Chrome and ChromeDriver

## Installation

1. **Install Python packages**:
   ```bash
   pip install pandas requests selenium beautifulsoup4
   ```

2. **Download ChromeDriver**:
   Ensure that the ChromeDriver version matches your installed version of Google Chrome. Download ChromeDriver from [here](https://sites.google.com/a/chromium.org/chromedriver/downloads) and place it in a directory included in your system's PATH.

3. **Set up 2Captcha API key**:
   Obtain an API key from [2Captcha](https://2captcha.com/), and replace the placeholder `'d4ce7f9fd51c4747cc03ec6f47fd0b1e'` in the script with your actual API key.

## Usage

1. **Prepare the Excel file**:
   - The script reads license numbers from an Excel file located at `C:\Users\bfrederick\OneDrive - Heartland Medical Sales and Service\Heartland\ASCSCRAP\TXASCS.xlsx`.
   - Ensure that the Excel file has a column named `LICENSE NUMBER` containing the license numbers.

2. **Run the script**:
   ```bash
   python script_name.py
   ```

## Script Explanation

1. **Loading the Excel File**:
   The script loads the Excel file into a DataFrame using `pandas`.

   ```python
   df = pd.read_excel(file_path, dtype=str)
   ```

2. **Setting Up Selenium**:
   The script configures Selenium to use Chrome in maximized mode.

   ```python
   chrome_options = webdriver.ChromeOptions()
   chrome_options.add_argument('--start-maximized')
   driver = webdriver.Chrome(options=chrome_options)
   ```

3. **Solving reCAPTCHA**:
   The `solve_recaptcha` function sends a request to 2Captcha to solve the reCAPTCHA and returns the solution.

   ```python
   def solve_recaptcha(site_key, page_url):
       ...
   ```

4. **Iterating Over License Numbers**:
   The script iterates over the license numbers from the specified starting index, performs the search, solves the reCAPTCHA, and retrieves the email addresses.

   ```python
   for index, lic_number in enumerate(lic_numbers[start_index:], start=start_index):
       ...
   ```

5. **Handling WebDriver Exceptions**:
   The script retries up to three times if a `WebDriverException` occurs.

   ```python
   except WebDriverException as e:
       ...
   ```

6. **Updating the Excel File**:
   After each email address is found, the script updates the Excel file with the new data.

   ```python
   df.to_excel(file_path, index=False)
   ```

## Notes

- Ensure that the necessary dependencies are installed and properly configured.
- The script uses hardcoded file paths and API keys. Modify these as needed to suit your environment.
- The script may need adjustments if the website structure changes or if the ChromeDriver version does not match the Chrome browser version.

## Troubleshooting

- **WebDriverException**: Ensure that ChromeDriver is correctly installed and that the version matches your installed Chrome browser.
- **2Captcha API issues**: Ensure that your API key is valid and that your account has sufficient balance.
- **Excel file path issues**: Verify that the file path is correct and that the Excel file is accessible.

## Contact

For any questions or issues, please contact the script author or refer to the documentation of the respective libraries and services used.

## Contribution

Contributions are welcome. Please submit a pull request or open an issue to discuss any changes.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
