from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import date
from datetime import timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv


# Date from file to add new dictionary for work
with open('database.csv', 'r', encoding="utf-16") as f:
    dict1 = {}
    reader = csv.reader(f, delimiter = ';')
    for row in reader:
        key = row[2]
        value = [row[3], row[5], row[6], row[4], row[0], row[1]]
        dict1[key] = value


# Feed list for block crawl feed
with open('database.csv', 'r', encoding="utf-16") as f:
    feed_list = []
    reader = csv.reader(f, delimiter = ';')
    feed_list = [row[4] for row in reader]


options = webdriver.ChromeOptions()
options.add_extension('ublock.crx')

driver = webdriver.Chrome(service = Service('chromedriver.exe'), options=options)
driver.implicitly_wait(7)

direct = 'https://direct.yandex.ru'


# Function for click on element, its needed for error handling
def click_element(driver, by, value):
    try:
        element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((by, value)))
        element.click()
    except Exception as e:
        print(f"Error clicking on element {value}: {e}")


# Function return answer for secret question in login page
def get_secret_question():
    with open('secret_question.txt', 'r') as f:
        return f.read()


def log_in(item):
    # Check first iteration and not clear cache
    if dict1[item.split('&ulogin=')[1]][0] == 'Волгоград':
        pass
    else:
        driver.close()
        driver.start_session({})
        driver.maximize_window()
    try:
        # Go to link direct
        driver.get(url=direct)
        click_element(driver, By.CSS_SELECTOR, 'span.lc-header-lpc__login-label') # Button 'Войти' in start page
        click_element(driver, By.CSS_SELECTOR, '[data-type="login"]') # Button 'Почта' in login form
        mail_input_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, 'login'))) # Field 'Логин или email' in login page
        mail_input_field.send_keys(dict1[item.split('&ulogin=')[1]][4])
        mail_input_field.send_keys(Keys.ENTER)
        pass_input_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, 'passwd'))) # Field 'Введите пароль' in login page
        pass_input_field.send_keys(dict1[item.split('&ulogin=')[1]][5])
        pass_input_field.send_keys(Keys.ENTER)
        time.sleep(1)
    except Exception as ex:
        pass
    
    # If yandex offers to log in using your fingerprint
    try:
        driver.find_element(By.CSS_SELECTOR, '[data-t="button:pseudo"]').click() # Button 'Не сейчас' in login page
    except Exception as ex:
        pass

    # If yandex asks about your favorite musician
    try:
        field_family_favorites_music = WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.NAME, 'question'))) # Field 'Введите любимого музыканта' in login page
        field_family_favorites_music.send_keys(get_secret_question())
        field_family_favorites_music.send_keys(Keys.ENTER)
        time.sleep(1)
    except Exception as ex: 
        pass


def crowling_ivashin():

    today = date.today()
    start = today - timedelta(days=today.weekday(), weeks=1)
    end = start + timedelta(days=6)

    with open('Links_list.txt', 'r', encoding='utf-8') as fp:
        ivashin_list = fp.read().splitlines()
        ivashin_result_list = [[f'{str(start.strftime("%d.%m.%y"))}-{str(end.strftime("%d.%m.%y"))}', 'Аккаунты', 'Фиды', 'РСЯ']] # Writing the header for table

        # Search adv block
        for item in ivashin_list[0:-2]:
            log_in(item)
            try:
                i_list = []
                driver.get(url = item)
                i_list.append(dict1[item.split('&ulogin=')[1]][0]) # Writing the city
                i_list.append(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-testid="StatsTotalCell.costWithTax"] .NumberText_number_text__l1krv'))).text.replace(' ', '')) # Writing data about the expenses in company page
                print(f"Accounts append {dict1[item.split('&ulogin=')[1]][0]} successfully")
                ivashin_result_list.append(i_list)
                
            except Exception as ex:
                print(ex)
                print(f"Error add element {dict1[item.split('&ulogin=')[1]][0]}")
                i_list.append(item)
                ivashin_result_list.append(i_list)
                continue

        print('\n'.join(map(str, ivashin_result_list)))
    

        # Goods gallery block
        log_in(ivashin_list[-2])
        driver.get(url = ivashin_list[-2])
        
        for region in dict1:
            if dict1[region][3] != '-':
                find_input_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input.Textinput-Control'))) # Field search by name company in company page
                find_input_field.click()
                
                find_input_field.click()
                find_input_field.send_keys(dict1[region][3])
                find_input_field.send_keys(Keys.ENTER)
                time.sleep(1)
                for inner_lst in ivashin_result_list:
                    if dict1[region][0] in inner_lst:
                        inner_lst.append(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-testid="StatsTotalCell.costWithTax"] .NumberText_number_text__l1krv'))).text.replace(' ', '')) # Writing Data about the expenses in company page
                        break

                else:
                    i_list = []
                    i_list.append(dict1[region][0])
                    i_list.append('0,00')
                    i_list.append(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-testid="StatsTotalCell.costWithTax"] .NumberText_number_text__l1krv'))).text.replace(' ', '')) # Writing Data about the expenses in company page
                    ivashin_result_list.append(i_list)
 
                find_input_field.send_keys(Keys.CONTROL + 'a')
                find_input_field.send_keys(Keys.BACKSPACE)
                time.sleep(1)
        
        


        print('\n'.join(map(str, ivashin_result_list)))

        print(f"All feeds append successfully")


        # Rsya block
        log_in(ivashin_list[-1])
        driver.get(url=ivashin_list[-1])

        click_element(driver, By.XPATH, "//span[contains(text(), 'Статистика')]") # Button 'Статистика' in company page
        click_element(driver, By.XPATH, "//span[contains(text(), 'Мастер отчетов')]") # Button 'Мастер отчетов' in company page
        click_element(driver, By.CSS_SELECTOR, 'div.b-statistics-form__period-group [role="listbox"]') # Button 'Группировка' in master company page
        click_element(driver, By.XPATH, "//span[contains(text(), 'за выбранный период')]") # Select 'за выбранный период' in master company page
        click_element(driver, By.CSS_SELECTOR, '[class="b-date-range-picker b-date-range-picker_type_super b-statistics-form__range-picker b-statistics-form__range-picker_type_a i-bem b-date-range-picker_js_inited"] > :nth-child(1)') # Button date selector in master company page
        
        date_from_field = driver.find_element(By.XPATH, '//*[@class="input__control super-calendar__from super-calendar__from-selected"]') # Field date from in master company page
        date_from_field.send_keys(Keys.CONTROL + 'a')
        date_from_field.send_keys(Keys.BACKSPACE)
        date_from_field.send_keys(str(start.strftime("%d.%m.%Y"))) # Entering the first day of last week
        date_from_field.send_keys(Keys.TAB) # Don't touch this is important to find next selector
        date_to_field = driver.find_element(By.XPATH, '//*[@class="input__control super-calendar__to super-calendar__to-selected"]') # Field date to in master company page
        date_to_field.send_keys(Keys.CONTROL + 'a')
        date_to_field.send_keys(Keys.BACKSPACE)
        date_to_field.send_keys(str(end.strftime("%d.%m.%Y"))) # Entering the last day of last week
        date_to_field.send_keys(Keys.ENTER)
        
        click_element(driver, By.CSS_SELECTOR, '[class="goals-selector goals-selector_initial-empty_yes b-statistics-form__goals-select i-bem goals-selector_js_inited"] > [type="button"]') # Button 'Данные по целям' in company page
        click_element(driver, By.XPATH, "//div[contains(text(), 'Значимые действия')]") # Select 'Значимые действия' in master company page
        click_element(driver, By.CSS_SELECTOR, '[class="goals-selector goals-selector_initial-empty_yes b-statistics-form__goals-select i-bem goals-selector_js_inited"] > [type="button"]') # Button 'Данные по целям' in company page
        click_element(driver, By.ID, 'labelwith_nds') # Checkbox 'c учётом НДС' in master company page
        
        for region in dict1:
            if dict1[region][0] == 'Волгоград':
                pass
            elif dict1[region][0] in ['-', 'Новороссия']:
                continue
            else:
                click_element(driver, By.XPATH, "//a[contains(text(), 'Мастер отчетов')]") # Button "Мастер отчётов" in master company page
                click_element(driver, By.CSS_SELECTOR, '[class="goals-selector goals-selector_initial-empty_yes b-statistics-form__goals-select i-bem goals-selector_js_inited"] > [type="button"]') # Button 'Данные по целям' in company page
                click_element(driver, By.XPATH, "//div[contains(text(), 'Значимые действия')]") # Select 'Значимые действия' in master company page

            click_element(driver, By.CSS_SELECTOR, '[class="dropdown dropdown_action_closed b-statistic-filters-editor__dropdown b-statistic-filters-editor__dropdown_type_filters-chooser i-bem"] > [type="button"]') # Button "Условие фильтрации" in master company page
            
            field_find_in_filter_condition = driver.find_element(By.CSS_SELECTOR, '[placeholder="Искать условие"]') # Field "Искать условие" in master company page  
            field_find_in_filter_condition.send_keys('Регион таргетинга')
            click_element(driver, By.XPATH, "//i[contains(text(), 'Регион таргетинга')]") # Choise "Регион данных" data in master company page
            click_element(driver, By.CSS_SELECTOR, '[class="b-outboard-controls__switcher i-bem"]') # Button "Уточнить" in master company page

            find_field_region_rsya = (driver.find_element(By.XPATH, '//*[@placeholder="Найти регион"]')) # Field "Найти регион" in master company page
            find_field_region_rsya.click()
            find_field_region_rsya.send_keys(dict1[region][1]) # Writing regions name in find field as "Республика Дагестан"
            find_field_region_rsya.send_keys(Keys.ENTER)
            time.sleep(1)
            
            if dict1[region][0] != 'Краснодар':

                click_element(driver, By.XPATH, dict1[region][2]) # Click to the regions name in select list in find field as "Республика Дагестан"
                time.sleep(1)
                click_element(driver, By.CSS_SELECTOR, '[class="button button_theme_action button_size_s b-outboard-controls__accept-button popup__accept-button i-bem button_js_inited"]') # Click to OK in popup with choose region as "Республика Дагестан" in master company page
                click_element(driver, By.CSS_SELECTOR, '[class="b-layout-form__row b-layout-form__row_type_submit"] > :nth-child(2)') # Button show in popup with choose region as "Республика Дагестан" in master company page
                

            #Special condition for excluding the city of Sochi from Krasnodar region
            elif dict1[region][0] == 'Краснодар':
                
                click_element(driver, By.CSS_SELECTOR, '[class="checkbox checkbox_size_s checkbox_theme_normal checkbox_view_classic checkbox_lines_multi b-regions-tree__region-checkbox b-regions-tree__region-checkbox_id_10995 i-bem checkbox_js_inited"]') # Click to checkbox  on "Краснодарский край"  in popup with choose region in master company page
                
                click_element(driver, By.CSS_SELECTOR, '[class="checkbox checkbox_size_s checkbox_theme_normal checkbox_view_classic checkbox_lines_multi b-regions-tree__region-checkbox b-regions-tree__region-checkbox_id_239 i-bem checkbox_js_inited checkbox_checked_yes"]') # Unclick checkbox "Сочи" from Krasnodar region in popup with choose region in master company page
                time.sleep(1)
                click_element(driver, By.CSS_SELECTOR, '[class="button button_theme_action button_size_s b-outboard-controls__accept-button popup__accept-button i-bem button_js_inited"]') # Click to OK in popup with choose region as "Республика Дагестан" in master company page
                
                click_element(driver, By.CSS_SELECTOR, '[class="b-layout-form__row b-layout-form__row_type_submit"] > :nth-child(2)') # Button show in popup with choose region as "Республика Дагестан" in master company page
                
                
            for inner_lst in ivashin_result_list:
                if dict1[region][0] in inner_lst:
                    try:
                        inner_lst.append(driver.find_element(By.CSS_SELECTOR, '[class="b-stat-table__row b-stat-table__row_summary_yes"] :nth-child(5) > .b-stat-table__comparison-result').text.replace(' ', '')) # Writing data about the expenses in master company page
                    except:
                        inner_lst.append("0,00")
                        pass
                
            print(f"RSYA append {dict1[region][0]} successfully")
        
        print('\n'.join(map(str, ivashin_result_list)))


    with open('final_result_list.csv', 'w') as f:
        writer = csv.writer(f, delimiter = ';', lineterminator = '\n')
        for item in ivashin_result_list:
            writer.writerow(item)



try:
    start_time = time.time() # Записываем время выполнения скрипта
    driver.get(url=direct)
    driver.maximize_window()
    crowling_ivashin()
    print('Crowling Done')
    end_time = time.time() # Записываем время выполнения скрипта
    result_time = end_time - start_time
    minutes_time = int(result_time // 60)
    seconds_time = result_time % 60
    print(f'The script was executed in {minutes_time}:{seconds_time:2.0f}')
except Exception as ex:
    print(ex)
    pass

finally:
    driver.close()
    driver.quit()