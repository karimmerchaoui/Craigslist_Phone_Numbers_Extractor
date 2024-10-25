import requests
from bs4 import BeautifulSoup
from data_management import save_to_excel, extract_phone_numbers
from vpn_manager import connect,disconnect
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException, StaleElementReferenceException, UnexpectedAlertPresentException
from requests.exceptions import ConnectTimeout, ConnectionError, ReadTimeout
import random
import time
from fake_useragent import UserAgent
from vpn_manager import is_nordvpn_running
from data_management import get_location

class Scraper:
    def __init__(self, update_progress_callback,update_state_callback,log_message):
        self.update_progress = update_progress_callback
        self.update_state = update_state_callback
        self.log_message = log_message



    def get_posts(self,soup1):
        links = []
        l = len(soup1)
        for j, i in enumerate(soup1):

            self.update_progress(int((j / l) * 100))
            a = i.find('a')
            h = a.get('href')
            try:
                resume_page = requests.get(h, timeout=10)
                soup2 = BeautifulSoup(resume_page.text, "html.parser")
                posting_body_a = soup2.select_one("#postingbody a")
                if posting_body_a and posting_body_a.get('href') == '#':
                    links.append(h)
            except requests.exceptions.RequestException as e:
                self.log_message(f"Error accessing {h}: {e}")
        return links



    def run_scraping(self,new_city, new_state, distance):
        if not is_nordvpn_running():
            self.log_message("Please Open your VPN.")
            return
        self.update_state("Extracting Posts ...")


        geo_location=get_location(new_city,new_state)
        new_lat =geo_location.latitude
        new_lon = geo_location.longitude
        new_city = new_city.replace(' ', '-').lower()
        url = f"https://jerseyshore.craigslist.org/search/{new_city}-{new_state}/rrr?lat={new_lat}&lon={new_lon}&search_distance={distance}#search=1~thumb~0~0"
        self.log_message(url)
        try:
            listing_page = requests.get(url,timeout=10)
        except ConnectTimeout:
            self.log_message("The connection to the server timed out. Please try again.")
            return
        except ConnectionError:
            self.log_message("There was a problem connecting to the internet. Please check your connection.")
            return
        except ReadTimeout:
            self.log_message("There was a problem connecting to the internet. Please check your connection.")
            return

        soup1 = BeautifulSoup(listing_page.text, "html.parser")
        soup1 = soup1.find_all("li", class_="cl-static-search-result")
        links = self.get_posts(soup1)
        self.update_progress(0)
        l=len(links)
        j=0
        b=0
        self.log_message(f"Found {l} Posts with a Phone Number.")
        options = webdriver.ChromeOptions()
        options.add_argument('--start-minimized')
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument('--window-size=500,500')
        options.add_argument("--disable-gpu")
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_argument("--ignore-certificate-errors")
        ua = UserAgent()
        self.update_state("Scrapping Phone Numbers ... ")
        for i in links:

            disconnect()
            connect()
            time.sleep(10)
            random_user_agent = ua.random
            options.add_argument(f'user-agent={random_user_agent}')

            try:
                driver = webdriver.Chrome(options=options)
                driver.get("https://newjersey.craigslist.org/")
                driver.get(i)
                time.sleep(random.uniform(1, 3))
                self.log_message(f"Navigating to link: {i}")
                time.sleep(random.uniform(2, 4))
                save = True
                button_xpath = '//*[@id="postingbody"]/a'

            except ConnectTimeout:
                self.log_message("The connection to the server timed out. Please try again.")
                return
            except ConnectionError:
                self.log_message("There was a problem connecting to the internet. Please check your connection.")
                return
            except ReadTimeout:
                self.log_message("There was a problem connecting to the internet. Please check your connection.")
                return
            except WebDriverException:
                print(1)
                links.append(i)
                continue


            try:
                button = driver.find_element(By.XPATH, button_xpath)
                actions = ActionChains(driver)
                while True:
                    try:
                        actions.move_to_element(button).click().perform()
                        time.sleep(random.uniform(2, 6))
                        b=b+1
                        if b == 10:
                            save=False
                            links.append(i)
                            break
                    except StaleElementReferenceException:
                        break
                    except UnexpectedAlertPresentException:
                        save=False
                        links.append(i)
                        break
                    except WebDriverException:
                        save=False
                        links.append(i)
                        break
                    except Exception as e:
                        print(e)
                        save=False
                        links.append(i)
                        break


                if save:
                    description_text_element = driver.find_element(By.ID, 'postingbody')
                    title_text_element = driver.find_element(By.XPATH, '/html/body/section/section/h1/span')
                    postDate = driver.find_element(By.XPATH, '//*[@id="display-date"]/time')
                    d = description_text_element.text
                    t = title_text_element.text
                    p = extract_phone_numbers(d)
                    posted=element_title = postDate.get_attribute('innerText')
                    save_to_excel(t, d, p,posted, new_city, new_state, distance)
                    j=j+1
                    self.update_progress(int((j / l) * 100))

            except UnexpectedAlertPresentException:
                links.append(i)
                continue
            except NoSuchElementException as e:
                self.log_message(f"No such element found: {e}")
                links.append(i)
            except TimeoutException:
                links.append(i)
            finally:
                disconnect()
                try :
                    driver.refresh()
                    time.sleep(1)
                    driver.delete_all_cookies()
                    driver.refresh()
                except UnexpectedAlertPresentException:
                    links.append(i)
                    continue
                b=0
                driver.quit()
        self.update_progress(100)
        self.log_message("SCRAPING FINISHED")

