from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import selenium.common.exceptions
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import time, requests, os
from bs4 import BeautifulSoup as bs

class SeleniumActions:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option("detach", True)
        self.options.add_argument('--ignore-certificate-errors')
        self.driver = webdriver.Chrome(options=self.options)

    def open_url(self, url):
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )

    def login(self, username, password):
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="loginForm"]/div/div[1]/div/label/input')))

        #login on site
        self.driver.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[1]/div/label/input').send_keys(username)
        self.driver.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[2]/div/label/input').send_keys(password)
        self.driver.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[3]').click()

        #skipping two useless windows
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section/main/div/div/div/section/div/button')))
        self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section/main/div/div/div/section/div/button').click()

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/button[2]')))
        self.driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/button[2]').click()

    def first_post(self, url):
        # get first post
        self.driver.get(url)
        while True:
            try:
                time.sleep(5)
                self.driver.find_element(By.XPATH, '//button[@aria-label="Далі"]').click()

                time.sleep(1)
            except NoSuchElementException:
                break


        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, '_aagw')))
        self.driver.find_element(By.CLASS_NAME, '_aagw').click()

    def next_post(self):
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, '_abl-')))
            next = self.driver.find_element(By.CLASS_NAME, '_abl-')
            return next
        except selenium.common.exceptions.NoSuchElementException:
            return 0    

            
    def download_allposts(self, url): 
        self.first_post(url)

        user_name = url.split('/')[-1]

        # check if folder corresponding to user name exist or not
        if(os.path.isdir(user_name) == False):
    
            # Create folder
            os.mkdir(user_name)

        # Check if Posts contains multiple images or videos
        multiple_images = self.nested_check()
        

        if multiple_images:
            print('1')
            nescheck = multiple_images
            count_img = 0
            
            while nescheck:
                elem_img = self.driver.find_element(By.CSS_SELECTOR, 'div._aamm')
    
                # Function to save nested images
                self.save_multiple(user_name+'/'+'content1.'+str(count_img), elem_img)
                count_img += 1
                nescheck.click()
                nescheck = self.nested_check()
    
            # pass last_img_flag True
            self.save_multiple(user_name+'/'+'content1.' +
                        str(count_img), elem_img, last_img_flag=3)
        else:
            print('2')
            self.save_content('_aagv', user_name+'/'+'content1')
        c = 2

        while(True):
            next_el = self.next_post()
            
            if next_el != False:
                next_el.click()
                time.sleep(1.3)
                
                try:
                    multiple_images = self.nested_check()
                    
                    if multiple_images:
                        nescheck = multiple_images
                        count_img = 0
                        
                        while nescheck:
                            elem_img = self.driver.find_element(By.CSS_SELECTOR, 'div._aamm')
                            self.save_multiple(user_name+'/'+'content' +
                                        str(c)+'.'+str(count_img), elem_img)
                            count_img += 1
                            nescheck.click()
                            nescheck = self.nested_check()
                        self.save_multiple(user_name+'/'+'content'+str(c) +
                                    '.'+str(count_img), elem_img, 1)
                    else:
                        self.save_content('_aagv', user_name+'/'+'content'+str(c))
                
                except selenium.common.exceptions.NoSuchElementException:
                    print("finished")
                    return
            
            else:
                break
            
            c += 1


    def save_content(self, class_name, img_prefix):
        time.sleep(0.5)
        try:
            pic_elements = self.driver.find_elements(By.CLASS_NAME, class_name)
        except selenium.common.exceptions.NoSuchElementException:
            print("Either This user has no images or you haven't followed this user or something went wrong")
            return

        # Створюємо список для зберігання посилань на фотографії
        photo_links = []

        for pic in pic_elements:
            html = pic.get_attribute('innerHTML')
            soup = bs(html,'html.parser')
            link = soup.find('video')
            if link:
                link = link['src']
            else:
                link = soup.find('img')['src']
            photo_links.append(link)

        # Визначаємо останнє посилання
        last_photo_link = photo_links[-1]

        # Завантажуємо останню фотографію
        response = requests.get(last_photo_link)

        # Зберігаємо її у файл
        img_name = img_prefix + '.jpg'
        with open(img_name, 'wb') as f:
            f.write(response.content)
    
    def save_multiple(self, img_name, elem, last_img_flag=False):
        time.sleep(1)
        l = elem.get_attribute('innerHTML')
        html = bs(l, 'html.parser')
        biglist = html.find_all('ul')
        biglist = biglist[0]
        list_images = biglist.find_all('li')
        if last_img_flag:
            user_image = list_images[-1]
        else:
            user_image = list_images[(len(list_images) // 2)]
        video = user_image.find('video')
        if video:
            link = video['src']
        else:
            link = user_image.find('img')['src']
        response = requests.get(link)
        with open(img_name+'.jpg', 'wb') as f:
            f.write(response.content)

    def next_post(self):
        try:
            # nex = self.driver.find_element(By.CLASS_NAME, '_abl-')
            div_element = self.driver.find_element(By.CLASS_NAME, '_aaqg')
            nex = div_element.find_element(By.CLASS_NAME, '_abl-')
            return nex
        except selenium.common.exceptions.NoSuchElementException:
            return 0
        
    def nested_check(self):
        try:
            time.sleep(1)
            nes_nex = self.driver.find_element(By.XPATH, '//button[@aria-label="Далі"]')
            return nes_nex
        
        except selenium.common.exceptions.NoSuchElementException:
            return 0


url = 'https://instagram.com/' + input('Enter User Name Of User For Downloading Posts:')
selenium_actions = SeleniumActions()
selenium_actions.open_url("https://www.instagram.com/")
selenium_actions.login("USERNAME", "PASSWORD")
selenium_actions.download_allposts(url)
