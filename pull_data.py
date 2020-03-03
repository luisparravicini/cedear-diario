from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from pathlib import Path
import json


def pull_stock_list_from_web(file):
    return list()


stocks_list_path = Path('stocks.json')
if stocks_list_path.exist():
    with open(stocks_list_path) as file:
        stocks = json.loads(file)
else:
    stocks = pull_stocks_from_web()

listing_url = 'https://www.invertironline.com/Mercado/Cotizaciones'

driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
driver.get(listing_url)

elem = Select(driver.find_element_by_id('paneles'))
elem.select_by_visible_text('CEDEARs')

wait = WebDriverWait(driver, 10)
expected_text = 'Acciones Argentina - Panel CEDEARs'
selector = (By.ID, 'header-cotizaciones')
condition = EC.text_to_be_present_in_element(selector, expected_text)
element = wait.until(condition)

select_elem = wait.until(EC.presence_of_element_located((By.XPATH, '//select[@name="cotizaciones_length"]')))
elem = Select(select_elem)
elem.select_by_visible_text('Todo')


INDEX_TOTAL = 11
INDEX_SYMBOL = 0

table = driver.find_element_by_id('cotizaciones')
rows = table.find_elements(By.TAG_NAME, 'tr')
headers = rows[0].find_elements_by_tag_name('td')
assert headers[INDEX_SYMBOL].text == 'Símbolo', f'unexpected header name [1]'
assert headers[INDEX_TOTAL].text == 'Monto\nOperado', f'unexpected header name [2]'

stocks = list()
for row in rows[1:-1]:
    cols = row.find_elements_by_tag_name('td')

    name = cols[INDEX_SYMBOL].text.split("\n")[0]
    assert len(name) > 0, f'"{name}" too short'

    total = int(cols[INDEX_TOTAL].text.replace('.', ''))

    stocks.append({'total': total, 'node': cols[INDEX_SYMBOL], 'name': name})


print(stocks)
print(len(stocks))
#driver.close()
