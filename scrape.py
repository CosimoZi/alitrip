# coding: utf-8
from __future__ import unicode_literals
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import datetime
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
import traceback


def get_page(params):
    # service_args = [
    #     '--proxy=127.0.0.1:8979',
    #     '--proxy-type=http',
    # ]
    # driver = webdriver.PhantomJS(
    #     service_args=service_args
    # )
    # # driver=webdriver.Firefox()
    try:
        date, (depCity, arrCity), driver = params
        print date, depCity, arrCity
        wait = WebDriverWait(driver, 10)
        if 'sijipiao.alitrip.com/ie/flight_search_result.htm' not in driver.current_url:
            driver.get('https://sijipiao.alitrip.com/ie/flight_search_result.htm')
        print 'get start page'
        # wait.until(EC.presence_of_element_located((By.CLASS_NAME,'J_DepCity')))
        # wait.until(EC.presence_of_element_located((By.XPATH,'//*[@name="tripType" and @class="search-input J_Radio"]')))
        sel = Select(driver.find_element_by_xpath('//*[@name="tripType" and @class="search-input J_Radio"]'))
        sel.select_by_value('1')
        print 'filling in depCity'
        driver.find_element_by_class_name('J_DepCity').click()
        driver.find_element_by_class_name('J_DepCity').clear()
        driver.find_element_by_class_name('J_DepCity').send_keys(depCity)
        sleep(0.5)
        driver.find_element_by_class_name('J_DepCity').send_keys(Keys.ENTER)
        driver.find_element_by_class_name('J_DepCity').send_keys(Keys.TAB)
        print 'filling in arrCity'
        driver.find_element_by_class_name('J_ArrCity').clear()
        driver.find_element_by_class_name('J_ArrCity').send_keys(arrCity)
        sleep(0.5)
        driver.find_element_by_class_name('J_ArrCity').send_keys(Keys.ENTER)
        driver.find_element_by_class_name('J_ArrCity').send_keys(Keys.TAB)
        print 'filling in DepDate'
        driver.find_element_by_class_name('J_DepDate').clear()
        driver.find_element_by_class_name('J_DepDate').send_keys(date[0])
        driver.find_element_by_class_name('J_DepDate').send_keys(Keys.TAB)
        print 'filling in EndDate'
        sleep(0.5)
        driver.find_element_by_class_name('J_EndDate').clear()
        driver.find_element_by_class_name('J_EndDate').send_keys(date[1])
        driver.find_element_by_class_name('J_EndDate').send_keys(Keys.TAB)
        print 'posting'
        driver.find_element_by_class_name('search-btn').click()
        # driver.find_element_by_class_name('search-btn').send_keys(Keys.RETURN)
        # element.clear()
        # element.send_keys(date[0])
        # # driver.find_element_by_class_name('J_DepDate').send_keys(Keys.TAB)
        # element = driver.find_element_by_class_name('J_EndDate')
        # element.clear()
        # element.send_keys(date[1],Keys.RETURN)
        # wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'search-btn')))
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'search-msg')))
        # sleep(5)
        # driver.get_screenshot_as_png()
        # driver.save_screenshot('test.png')
        # driver.close()
    except:
        # driver.get_screenshot_as_png()
        # driver.save_screenshot('test.png')
        print 'retrying'
        traceback.print_exc()
        # raise
        get_page(params)
        # traceback.print_exc()
        # driver.close()
    print 'finished'


    # AlitripSpider.get_page(('2016-09-10', '2016-09-12'), '北京', '旧金山')


def get_params():
    soup = BeautifulSoup(open('schema_int.xml').read(), 'lxml')
    cities = []
    for i in soup.find_all('p'):
        # print i
        cities.append((i['dpttrich'], i['dsttrich']))
    dates = []
    for i in (9, 15, 23, 32, 47, 87):
        depday = datetime.datetime.today().date() + datetime.timedelta(i)
        for j in (7, 8, 9, 14, 21):
            arrday = depday + datetime.timedelta(j)
            dates.append((depday.strftime('%Y-%m-%d'), arrday.strftime('%Y-%m-%d')))
            # days.append(day.strftime('%Y-%m-%d'))
    params = []
    for date in dates:
        for city in cities:
            params.append((date, city))
    return params


params = get_params()
service_args = [
    '--proxy=localhost:8979',
    '--proxy-type=http',
    # '--ssl-client-certificate-file=/Users/cosimo/Downloads/mitmproxy-ca-cert.pem',
    '--ssl-protocol=any', '--ignore-ssl-errors=true', '--web-security=false'
]


def run_a_process(params):
    driver = webdriver.PhantomJS(service_args=service_args)
    # driver = webdriver.Firefox()
    try:
        for param in params:
            try:
                get_page(param + (driver,))
            except:
                raise
                continue
    except:
        driver.close()
        raise
    driver.close()
    return 0


if __name__ == '__main__':
    n = 1
    pool = ThreadPool(processes=n)
    split_list=lambda n, l: [l[len(l) / n * i:len(l) / n * (i + 1)] for i in range(n)]
    # first_part=split_list(n,params)[0]
    # run_a_process(first_part)
    # print first_part
    # run_a_process(first_part)
    # run_a_process(split_list(n, params)[0][0])
    # print split_list(n,params)
    pool.map_async(run_a_process, split_list(n,params))
    pool.close()
    pool.join()
