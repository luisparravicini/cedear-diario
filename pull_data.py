from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from pathlib import Path
import json
import re
import datetime


def pull_stocks_list(driver, base_url, path):
    print('downlading stocks list')

    driver.get(base_url + 'Mercado/Cotizaciones')

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

    table = driver.find_element_by_id('cotizaciones')
    rows = table.find_elements(By.TAG_NAME, 'tr')

    INDEX_TOTAL = 11
    INDEX_SYMBOL = 0

    headers = rows[0].find_elements_by_tag_name('td')
    assert headers[INDEX_SYMBOL].text == 'Símbolo', f'unexpected header name [1]'
    assert headers[INDEX_TOTAL].text == 'Monto\nOperado', f'unexpected header name [2]'

    stocks = list()
    for row in rows[1:-1]:
        cols = row.find_elements_by_tag_name('td')

        name = cols[INDEX_SYMBOL].text.split("\n")[0]
        assert len(name) > 0, f'"{name}" too short'

        total = int(cols[INDEX_TOTAL].text.replace('.', ''))

        link = cols[INDEX_SYMBOL].find_element_by_tag_name('a')
        assert link is not None, f'link not found for {name}'
        href = link.get_attribute('href')

        stocks.append({'total': total, 'href': href, 'name': name})

    driver.close()

    stocks.sort(key=lambda x: x['total'])
    MAX_STOCKS = 15
    result = stocks[-MAX_STOCKS:]
    for stock in result:
        del stock['total']

    return result


def download_graphic(driver, stock, out_dir):
    stock_dir = Path(out_dir, re.sub(r'\W', '_', stock['name']))
    stock_dir.mkdir(parents=True, exist_ok=True)

    svg_path = Path(stock_dir, 'graphic.svg')
    if svg_path.exists():
        print('\tsvg [skipped]')
        return

    print('\tsvg')
    driver.get(stock['href'])

    wait = WebDriverWait(driver, 10)
    selector = (By.CLASS_NAME, 'header-cotizaciones')
    condition = EC.presence_of_element_located((By.CLASS_NAME, "highcharts-container"))
    svg = wait.until(condition)
    assert svg is not None, 'svg not found'

    data = svg.get_attribute('innerHTML')

    tmp_path = Path(str(svg_path) + '.tmp')
    with open(tmp_path, 'w') as file:
        file.write(data)
    tmp_path.rename(svg_path)


def pull_quotes(driver, stocks):
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    out_dir = Path('data', today)

    for stock in stocks:
        print(stock['name'])
        download_graphic(driver, stock, out_dir)

    driver.close()


driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
base_url = 'https://www.invertironline.com/'
stocks_list_path = Path('stocks.json')
if stocks_list_path.exists():
    with open(stocks_list_path) as file:
        stocks = json.load(file)
else:
    stocks = pull_stocks_list(driver, base_url, stocks_list_path)
    with open(stocks_list_path, 'w') as file:
        json.dump(stocks, file)


pull_quotes(driver, stocks)




#driver.close()
