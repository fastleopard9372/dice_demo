from flask import Flask, render_template, request , abort
import json
import requests
import chromedriver_autoinstaller
import undetected_chromedriver as uc
import re
from selenium.webdriver.common.alert import Alert
from time import sleep
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from random import randint
from selenium import webdriver
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv
import asyncio

# chromedriver_autoinstaller.install() 

load_dotenv('config.env')

TWOCAPTCHA_API_KEY = os.getenv('TWOCAPTCHA_API_KEY')


all_count = 0
index = 0

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    
    # try:
        uid = request.form.get('uid')
        pwd = request.form.get('pwd')
        l = request.form.get('locate')
        f = request.form.get('filter')
        e = request.form.get('employement_type')
        p = request.form.get('posted_date')
        q = request.form.get('question')
        
        bot_run(uid,pwd,q,l,e,p)
        result = "bot running..."
        size ="www.dice.com"
        # json_string = json.dumps(data)
        return render_template('result.html',result = result,size = size)
    # except Exception as e:
    #     return str(e)


def solveCaptcha(driver):
    try:
        driver.find_element(By.CLASS_NAME,'captcha-solver-info').click()
        delay = 0
        while(delay < 120):
            captcha_status = driver.find_element(By.CLASS_NAME,'captcha-solver-info').text
            if('solved' in captcha_status.lower()):
                break
            else:
                sleep(5)
                delay += 5
        if(delay >= 120):
            print("Captcha solver failed")
            print("Moving to next one")
            return {'success' : False, 'msg':"Captcha solver failed. Moving to next one."}
            # continue
        return driver
    except:
        return driver

def login(driver,uid,pwd):
    url = 'https://www.dice.com/dashboard/login'
    try:
        driver.get(url)
        sleep(randint(1,3))

        email = driver.find_element(By.ID,'email')
        email.click()
        sleep(randint(7,15)/10.0)
        email.send_keys(uid)
        sleep(.5) 

        password = driver.find_element(By.ID,'password')
        password.click()
        sleep(randint(7,15)/10.0)
        password.send_keys(pwd)
        sleep(.5)     

        driver.find_element(By.XPATH, '//button[@type="submit"]').click()
        sleep(randint(40,50)/10.0)


    except Exception as e:
        print(e)
        driver.refresh()
        
    return driver

def move_element_pos(driver,element,offset = 0):
    element_location = element.location_once_scrolled_into_view
    top_position = element_location['y'] + driver.execute_script("return window.pageYOffset;")+offset
    driver.execute_script(f"window.scrollTo(0, {top_position})")
    sleep(.3)
    return top_position

def find_jobs(driver,q,l,e,p,start,index = 0):
    try:
        while (True):
            url = f" https://www.dice.com/jobs?q={q}&location={l}&filters.employmentType={e}&filters.postedDate={p}&radius=30&radiusUnit=mi&page={start}&pageSize=20&filters.easyApply=true&language=en"
            url = url.replace('|', '%7C')
            try:
                driver.get(url)
                sleep(randint(50,60)/10.0)
                if(index == 0):
                    all_count = driver.find_element(By.ID,'totalJobCount').text
                print(all_count)
                elements = driver.find_elements(By.XPATH,'//dhi-search-card[@data-cy="search-card"]')
                
                
                for element in elements:
                    try:
                        move_element_pos(driver, element,-150)
                        sleep(randint(10,20)/10.0)
                        # .find_elements(By.CLASS_NAME,'card-title-link')
                        if element.find_elements(By.CLASS_NAME,'ribbon-container'):
                            print ("applied")
                        else:
                            job_title = element.find_element(By.TAG_NAME, 'h5')
                            job_link = job_title.find_element(By.TAG_NAME, 'a')
                            job_title = job_link.text
                            job_link.click()
                            sleep(randint(30,40)/10.0)
                            all_window_handles = driver.window_handles
                            driver.switch_to.window(all_window_handles[1])
                            sleep(randint(40,50)/10.0)
                            
                            if 'dice.com/job-detail' in driver.current_url:
                                sleep(randint(30,40)/10.0)
                                cnt = len(driver.find_elements(By.ID, 'applyButton'))
                                while cnt==0:
                                    cnt = len(driver.find_elements(By.ID, 'applyButton'))
                                    continue
                                
                                driver.find_element(By.ID, 'applyButton').click()
                                sleep(randint(50,60)/10.0)
                                no_apply = 0
                                if 'dice.com/apply' not in driver.current_url:
                                    driver.close()
                                    all_window_handles = driver.window_handles
                                    if len(all_window_handles) > 0:
                                        driver.switch_to.window(all_window_handles[1])
                                    no_apply = 1
                                while ('dice.com/apply' in driver.current_url):
                                    btn_next = driver.find_element(By.CLASS_NAME,'btn-next')
                                    move_element_pos(driver, btn_next,-50)
                                    sleep(randint(5,8)/10.0)
                                    btn_next.click()
                                    sleep(randint(50,55)/10.0)
                                if('dice.com/application-submitted' in driver.current_url):
                                    if no_apply == 0:
                                        print (job_title)
                            driver.close()
                            driver.switch_to.window(all_window_handles[0])
                            sleep(randint(3,10)/10.0)
                        index += 1
                        if(index == all_count):
                            break
                    except Exception as e:
                        print(e)
                        all_window_handles = driver.window_handles
                        if len(all_window_handles) > 0:
                            driver.switch_to.window(all_window_handles[1])
                            driver.close()
                            driver.switch_to.window(all_window_handles[0])
                        else:
                            pass
                            sleep(2)
                    
                start += 20
                find_jobs(driver,q,l,e,p,start,index)
            except Exception as  e:
                print(e)
                driver.refresh()
    except:
        pass
    return driver

def bot_run(uid, pwd,q,l,e,p):
    driver= init_UC()
    # uid = 'davidsmith2024dev@gmail.com'
    # pwd = 'Dev@2024!@'
    # q = 'devops Engineers'
    # l = ''
    # e = "CONTRACTS|THIRD_PARTY"
    # p = 'SEVEN'
    driver = login(driver,uid,pwd)
    start = 0
    index = 0
    all_count = 0
    driver = find_jobs(driver,q,l,e,p,start,index)

def init_UC():
    chrome_options = uc.ChromeOptions()
    dir_path = os.getcwd()
    print(dir_path)
    chrome_options.add_argument(f"--load-extension={dir_path}/2captcha-solver")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--disable-setuid-sandbox')
    driver = uc.Chrome(driver_executable_path='chromedriver',options = chrome_options)

    sleep(5)
    try:
        driver.find_element(By.XPATH,'//input[@name="apiKey"]').click()
        while(True):
            try:
                driver.find_element(By.XPATH,'//input[@name="apiKey"]').click()
                sleep(.5)
                driver.find_element(By.XPATH,'//input[@name="apiKey"]').send_keys(TWOCAPTCHA_API_KEY)
                sleep(.5)
                driver.find_element(By.ID,'connect').click()
                sleep(1)
                WebDriverWait(driver, 10).until(EC.alert_is_present())
                driver.switch_to.alert.accept()
                break
            except:
                driver.refresh()
        sleep(2)
    except:
        if(driver.current_window_handle == driver.window_handles[0]):
            driver.switch_to.window(driver.window_handles[1])
        else:
            driver.switch_to.window(driver.window_handles[0])
        while(True):
            try:
                driver.find_element(By.XPATH,'//input[@name="apiKey"]').click()
                sleep(.5)
                driver.find_element(By.XPATH,'//input[@name="apiKey"]').send_keys(TWOCAPTCHA_API_KEY)
                sleep(.5)
                driver.find_element(By.ID,'connect').click()
                sleep(1)
                WebDriverWait(driver, 10).until(EC.alert_is_present())
                driver.switch_to.alert.accept()
                break
            except:
                driver.refresh()
        sleep(2)
    return driver

if __name__ == '__main__':
    app.run(debug=True)
