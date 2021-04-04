from enum import Enum
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)
driver.get('https://bills.parliament.uk/')

'''
-----------------------------------------------------------
Main set of classes used to intedface with the UK Parliament
Legislation Library.

TODO:
    - Support the options provided when you expand the form.

-----------------------------------------------------------
'''

class BillSession(Enum):
    ALL = {"value": "0", "name": "All"}
    S2019_21 = {"value": "35", "name": "2019-2021"}
    S2019_19 = {"value": "34", "name": "2019-2019"}
    S2017_19 = {"value": "30", "name": "2017-2019"}
    S2016_17 = {"value": "29", "name": "2016-2017"}
    S2015_16 = {"value": "28", "name": "2015-2016"}
    S2013_14 = {"value": "27", "name": "2013-2014"}
    S2012_13 = {"value": "25", "name": "2012-2013"}
    S2010_12 = {"value": "24", "name": "2010-2012"}
    S2009_10 = {"value": "23", "name": "2009-2010"}
    S2008_09 = {"value": "22", "name": "2008-2009"}
    S2007_08 = {"value": "21", "name": "2007-2008"}
    S2006_07 = {"value": "20", "name": "2006-2008"}
    S2005_06 = {"value": "19", "name": "2005-2006"}
    S2004_05 = {"value": "18", "name": "2004-2005"}
    


class SortOrder(Enum):
    BY_TITLE = {"value": "0", "name": "Title"},
    BY_NEWEST = {"value": "1", "name": "Newest"}
    BY_OLDERST = {"value": "2", "name": "Oldest"}

class BillType(Enum):
    ALL = {"value": "", "name": "All"}
    HYBRID = {"value": "4", "name": "Hybrid"}
    PRIVATE = {"value": "6", "name": "Private"}
    PUBLIC = {"value": "1,5,7,8,2,3", "name": "Public"}
    GOVERNMENT_BILL = {"value": "1", "name": "Government Bill"}
    PMB_TMR = {"value": "5", "name": "Private Members' Bill (under the Ten Mute Rule)"}
    PMB_BB = {"value": "7", "name": "Private Members' Bill (Ballot Bill)"}
    PMB_PB = {"value": "8", "name": "Private Members' Bill (Presentation Bill)"}
    PMB_HOL = {"value": "2", "name": "Private Members' Bill (Starting in the House of Lords)"}

class BillStage(Enum):
    ALL = {"value": "", "name": "All"}
    ACTIVE = {"value": "-1", "name": "Currently active"}
    FIRST_READING = {"value": "6,1", "name": "1st Reading"}
    SECOND_READING = {"value": "7,2", "name": "2nd Reading"}
    COMMITTEE_STAGE = {"value": "8,3", "name": "Committee Stage"}
    REPORT_STAGE = {"value": "9,4", "name": "Report Stage"}
    THIRD_READING = {"value": "10,5", "name": "3rd Reading"}
    ROYAL_ASSENT = {"value": "11", "name": "Royal Assent"}

class CurrentHouse(Enum):
    HOL = {"value": "2", "name": "House of Lords"}
    HOC = {"value": "1", "name": "Hosue of Commons"}
    BOTH = {"value": "", "name": "All"}
    NEITHER = {"value": "3", "name": "Not before either House"}

'''
Used to interact with the search form on the bills website.
'''
class SearchForm():
    def __init__(self, driver: webdriver.Chrome):
        try:
            self.driver = driver
            self.bill_title_input: WebElement = driver.find_element_by_id('SearchTerm')
            self.session_input: Select = Select(driver.find_element_by_id('Session'))
            self.bill_stage_input: Select = Select(driver.find_element_by_id('BillStage'))
            self.bill_sort_order_input: Select = Select(driver.find_element_by_id('BillSortOrder'))
            self.bill_type_input: Select = Select(driver.find_element_by_id('BillType'))
            self.current_house_input: Select = Select(driver.find_element_by_id('CurrentHouse'))
            self.search_button: WebElement = driver.find_element(by=By.CSS_SELECTOR, value="button[type=submit]")
        except Exception as err:
            raise err
     
    def set_bill_title(self, title: str):
        self.bill_title_input.clear()
        self.bill_title_input.send_keys(title)

    def set_session(self, bill_session: BillSession):
        self.session_input.select_by_value(bill_session.value['value'])

    def set_bill_stage(self, bill_stage: BillStage):
        options = self.bill_stage_input.options

        for option in options:
            opt: WebElement = option
            print(opt.get_attribute('value'))

        self.bill_stage_input.select_by_value(str(bill_stage.value['value']))

    def set_bill_type(self, bill_type: BillType):
        self.bill_type_input.select_by_value(bill_type.value['value'])

    def set_current_house(self, house: CurrentHouse):
        self.current_house_input.select_by_value(house.value['value'])

    def set_sort_order(self, order: SortOrder):
        self.bill_sort_order_input.select_by_value(order.value['value'])

    def search(self):
        self.search_button.click()
        return self.driver

form = SearchForm(driver)

bills: list[WebElement] = driver.find_elements_by_class_name('card-bill')
#Get bill name, last updated, session of introduction, orignation, and next stage.

'''
Used to retrieve relevant information from an entry from a search.
'''
class Bill():
    def __init__(self, bill):
        content: WebElement = bill.find_element_by_class_name('content')
        name_element: WebElement = content.find_element_by_class_name('primary-info')
        self.name = name_element.get_attribute('innerHTML')
        session_element = bill.find_element_by_class_name('secondary-info')
        self.session = session_element.get_attribute('innerHTML')
        infographic_element = bill.find_element_by_class_name('infographic')
        infographic_items = infographic_element.find_element_by_class_name('items')
        item_contents: list[WebElement] = infographic_element.find_elements_by_class_name('item')
        originated_element = item_contents[0]
        self.originated = originated_element.find_element_by_class_name('item-value').get_attribute('innerHTML')
        next_stage_element = item_contents[1]
        self.next_stage_label = next_stage_element.find_element_by_class_name('label').get_attribute('innerHTML').replace('Next Stage:', '').strip()
        self.next_stage_value = next_stage_element.find_element_by_class_name('item-value').get_attribute('innerHTML').replace('<br>', '')
        info_element = bill.find_element_by_class_name('info')
        last_updated_element = info_element.find_element_by_class_name('indicators-left')
        bill_type_element = info_element.find_element_by_class_name('indicators-right')
        #TODO: Turn this string date and time into a datetime object.
        self.last_updated = last_updated_element.get_attribute('innerHTML').replace('Last updated: ').strip()
        inner_bill_type_element = bill_type_element.find_element_by_class_name('indicator')
        self.bill_type = inner_bill_type_element.get_attribute('data-help-title').strip()

    def get_bill_name(self):
        return self.name

    def get_session_introduced(self):
        return self.session
    
    #Where the bill originated.
    def get_origination(self):
        return self.originated

    def get_next_stage(self):
        return self.next_stage_value

    def get_next_stage_type(self):
        return self.next_stage_label

    def get_bill_type(self):
        return self.bill_type

    def get_last_update_time(self):
        return self.last_updated

    #Clicks this bill entry on the headless browser.
    def click(self):
        pass

search = SearchForm(driver)
search.set_bill_title('dfafjakdfj')
search.search()

try:
    bills = driver.find_elements_by_class_name('card-bill')
    print(bills)
except NoSuchElementException as err:
    print('No such element exception')
