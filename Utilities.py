from flask.globals import current_app
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

from time import sleep

from Company import Company

from os import listdir, mkdir

from urllib.request import Request, urlopen

import pdfquery
from pdfquery.cache import FileCache

def convert_to_float(str):
    try:
        res = float(str)
        return res
    except:
        return str

def is_float(n):
    try:
        float(n)
        return True
    except:
        return False

def delete_invalid_data(data):
    new_data = [data[0]]

    for i in range(len(data)):
        if i == 0:
            continue
        
        if is_float(data[i]):
            new_data.append(data[i])

    return new_data

def get_data(pdf, data_string):
    # Get data
    try:
        label = pdf.pq(f'LTTextLineHorizontal:contains("{data_string}")')
        left_corner = float(label.attr('x0'))
        bottom_corner = float(label.attr('y0'))
    except:
        return []

    if data_string == "PER (X)" or data_string == "PBV (X)":
        data = pdf.pq('LTTextLineHorizontal:in_bbox("%s, %s, %s, %s")' % (left_corner, bottom_corner, left_corner+275, bottom_corner+8)).text().split()
    elif data_string == "DER(X)" or data_string == "ROE (%)":
        data = pdf.pq('LTTextLineHorizontal:in_bbox("%s, %s, %s, %s")' % (left_corner, bottom_corner, left_corner+325, bottom_corner+8)).text().split()

    # Sanitize Data
    if "PER" in data:
        del data[1]
        data[0] = "PER (X)"
    elif "PBV" in data:
        del data[1]
        data[0] = "PBV (X)"
        data = data[:6]
    elif "DER(X)" in data:
        data[0] = "DER (X)"
    elif "ROE" in data:
        del data[1]
        data[0] = "ROE (%)"

    # Change data to float
    for i in range(len(data)):
        data[i] = convert_to_float(data[i])
    
    data = delete_invalid_data(data)

    return data

def extract_data_from_pdf(url):
    current_dir = listdir()

    if "temp" not in current_dir:
        mkdir("temp")
    f = open('./temp/temp.pdf', 'wb')
    url_request = Request(url, 
                        headers={"User-Agent": "Mozilla/5.0"})
    webpage = urlopen(url_request).read()
    f.write(webpage)
    f.close()

    if "cache" not in current_dir:
        mkdir("cache")
    pdf = pdfquery.PDFQuery("./temp/temp.pdf",  parse_tree_cacher=FileCache("./cache/"))
    
    pdf.load()
    der = get_data(pdf, "DER(X)")
    pbv = get_data(pdf, "PBV (X)")
    roe = get_data(pdf, "ROE (%)")
    per = get_data(pdf, "PER (X)")
    
    return der, pbv, roe, per

def evaluate_data(der, pbv, roe, per):

    if len(der) == 0:
        der.append(None)
    
    if len(pbv) == 0:
        pbv.append(None)
    
    if len(roe) == 0:
        roe.append(None)
    
    if len(per) == 0:
        per.append(None)

    latest_data = {
        'der': der[len(der)-1],
        'pbv': pbv[len(pbv)-1],
        'roe': roe[len(roe)-1],
        'per': per[len(per)-1]
    }

    if latest_data['der'] != None and latest_data['der'] >= 1:
        return False
    
    if latest_data['pbv'] != None and latest_data['pbv'] >= 1:
        return False

    if latest_data['roe'] != None and latest_data['roe'] <= 10:
        return False

    if latest_data['per'] != None and latest_data['per'] >= 10:
        return False
    
    return True

def dump(items, mode='txt', passed_only=True):
    if mode == 'txt':

        f = open('./Results.txt', 'w')
        f.close()

        f = open('./Results.txt', 'a')
        for item in items:
            if passed_only:
                if item.passed:
                    f.write(item.to_string())
            else:
                f.write(item.to_string())

    elif mode == 'excel':
        pass
    elif mode == 'sheets':
        pass

def scrape_companies():
    companies = []

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome('./driver/chromedriver.exe', options=chrome_options, service_log_path='NUL')

    driver.get('https://idx.co.id/data-pasar/laporan-statistik/ringkasan-performa-perusahaan-tercatat/')

    entries_option = driver.find_element_by_xpath('/html/body/main/div/div[3]/div[1]/label/select/option[4]')
    driver.execute_script("arguments[0].value = '999999';", entries_option)
    entries_combobox = Select(driver.find_element_by_name('performanceTable_length'))
    sleep(3)
    entries_combobox.select_by_visible_text('100')

    sleep(3)
    table = driver.find_elements_by_tag_name('tbody')[0]
    rows = table.find_elements_by_tag_name('tr')
    print("\nLoading", len(rows), "companies.")
    for i in range(len(rows)):
        cols = rows[i].find_elements_by_tag_name('td')
        company_code = cols[1].text
        company_name = cols[2].text
        pdf_link = cols[3].find_elements_by_tag_name('a')[0].get_attribute('href')

        der, pbv, roe, per = extract_data_from_pdf(pdf_link)
        passed = evaluate_data(der, pbv, roe, per)

        current_company = Company(i+1, company_code, company_name, pdf_link, passed, der, pbv, roe, per)

        print(f"\n({i+1}/{len(rows)})>", current_company.to_string())

        companies.append(current_company)
    
    driver.quit()
    return companies