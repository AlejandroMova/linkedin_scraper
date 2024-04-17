import os
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
import pickle
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import json
from seleniumbase import SB

load_dotenv()
user = os.getenv('USER')
password = os.getenv('PASSWORD')

def wait_for_element(driver, time, by, key): 
    # wait for an element
    wait_for = WebDriverWait(driver, time).until(
        EC.presence_of_element_located((by, key))
    )

def save_cookies(driver): 
    # get cookies from driver
    cookies = driver.driver.get_cookies()
  
    pickle.dump(cookies, open('cookies.pkl', 'wb'))

def load_cookies(driver): 
    try: 
        cookies = pickle.load(open('cookies.pkl', 'rb'))
        for cookie in cookies: 
            cookie['domain'] = 'www.linkedin.com'     
            try: 
                driver.driver.add_cookie(cookie)
            except Exception as e:
                pass
    except: 
        pass

def into_text(driver, class_search): 
    # this function searches for specific parts of the body of results, and then translates the webelement into text
    
    # get web elements, searching by class
    elements = driver.find_elements(By.CLASS_NAME, class_search)
    text = []

    # get the text of these elements, and transfer into list
    for i in range(len(elements)): 
        text.append(elements[i].text)
    

    return text

keyword = 'Ingeniero'
location = 'Ciudad de Mexico'

with SB(uc=True) as sb: 

    # open undetectable
    sb.driver.uc_open('https://www.linkedin.com/feed/')
    

    # load cookies
    load_cookies(sb)

    # login, if asked, if not go directly into feed for search
    if sb.is_text_visible("Iniciar sesión", "#organic-div > div.header__content > h1"): 
        #sb.click("body > div.page > main> div > p > a")
        sb.type("#username", user)
        sb.type("#password", password + '\n')
        sb.open_if_not_url("https://www.linkedin.com/feed/?trk=seo-authwall-base_sign-in-submit")
        save_cookies(sb)
        
    # search for keyword and location
    sb.driver.uc_open('https://linkedin.com/jobs/search/?keywords=' + keyword + '&location=' + location.replace(' ', '%20'))    

    # scroll to get more results
    frame = sb.find_element(By.CLASS_NAME, "job-card-container")
    scroll_origin = ScrollOrigin.from_element(frame)
    ActionChains(sb.driver).scroll_from_origin(scroll_origin, 0, 10000).perform()

    # get posts into dictionary
    cards_elements = sb.find_elements(By.CLASS_NAME, 'job-card-container')
    cards = {}
    for card in cards_elements: 
        title = card.find_element(By.CLASS_NAME, 'job-card-list__title').text
        primary_description = card.find_element(By.CLASS_NAME, 'job-card-container__primary-description').text
        location = card.find_element(By.CLASS_NAME, 'artdeco-entity-lockup__caption').text

        try: 
            evaluation_time = card.find_element(By.CLASS_NAME, 'job-card-container__job-insight-text').text
        except: 
            evaluation_time = 'None'
        cards[title] = primary_description, location, evaluation_time

    with open("cards.json", "w") as file: 
        json.dump(cards, file, separators=(',\n', ': '), ensure_ascii=False)
