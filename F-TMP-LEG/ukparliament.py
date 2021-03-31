from enum import Enum
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select

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

    class BillSession(Enum):
        ALL = {"id": "0", "name": "All"},
        S2019_21 = {"id": "35", "name": "2019-2021"},
        S2019_19 = {"id": "34", "name": "2019-2019"},
        S2017_19 = {"id": "30", "name": "2017-2019"},
        S2016_17 = {"id": "29", "name": "2016-2017"},
        S2015_16 = {"id": "28", "name": "2015-2016"},
        S2013_14 = {"id": "27", "name": "2013-2014"},
        S2012_13 = {"id": "25", "name": "2012-2013"},
        S2010_12 = {"id": "24", "name": "2010-2012"},
        S2009_10 = {"id": "23", "name": "2009-2010"},
        S2008_09 = {"id": "22", "name": "2008-2009"},
        S2007_08 = {"id": "21", "name": "2007-2008"},
        S2006_07 = {"id": "20", "name": "2006-2008"},
        S2005_06 = {"id": "19", "name": "2005-2006"},
        S2004_05 = {"id": "18", "name": "2004-2005"}

    class SortOrder(Enum):
        BY_TITLE = {"id": "0", "name": "Title"},
        BY_NEWEST = {"id": "1", "name": "Newest"}
        BY_OLDERST = {"id": "2", "name": "Oldest"}

    class BillType(Enum):
        ALL = {"id": "", "name": "All"},
        HYBRID = {"id": "4", "name": "Hybrid"},
        PRIVATE = {"id": "6", "name": "Private"},
        PUBLIC = {"id": "1,5,7,8,2,3", "name": "Public"},
        GOVERNMENT_BILL = {"id": "1", "name": "Government Bill"},
        PMB_TMR = {"id": "5", "name": "Private Members' Bill (under the Ten Mute Rule)"},
        PMB_BB = {"id": "7", "name": "Private Members' Bill (Ballot Bill)"},
        PMB_PB = {"id": "8", "name": "Private Members' Bill (Presentation Bill)"},
        PMB_HOL = {"id": "2", "name": "Private Members' Bill (Starting in the House of Lords)"}

    class BillStage(Enum):
        ALL = {"id": "", "name": "All"},
        ACTIVE = {"id": "-1", "name": "Currently active"},
        FIRST_READING = {"id": "6,1", "name": "1st Reading"},
        SECOND_READING = {"id": "7,2", "name": "2nd Reading"},
        COMMITTEE_STAGE = {"id": "8,3", "name": "Committee Stage"},
        REPORT_STAGE = {"id": "9,4", "name": "Report Stage"},
        THIRD_READING = {"id": "10,5", "name": "3rd Reading"},
        ROYAL_ASSENT = {"id": "11", "name": "Royal Assent"}

    class CurrentHouse(Enum):
        HOL = {"id": "2", "name": "House of Lords"},
        HOC = {"id": "1", "name": "Hosue of Commons"},
        BOTH = {"id": "", "name": "All"},
        NEITHER = {"id": "3", "name": "Not before either House"}
      
    def set_bill_title(self, title: str):
        self.bill_title_input.clear()
        self.bill_title_input.send_keys(title)

    def set_session(self, option_text: str):
        self.session_input.select_by_visible_text(option_text)

    def set_bill_stage(self, option_text: str):
        self.bill_stage_input.select_by_visible_text(option_text)

    def set_bill_type(self, option_text: str):
        self.bill_type_input.select_by_visible_text(option_text)

    def set_current_house(self, option_text: str):
        self.current_house_input.select_by_visible_text(option_text)

    def set_sort_order(self, option_text: str):
        self.bill_sort_order_input.select_by_visible_text(option_text)

    def search(self):
        self.search_button.click()
        return self.driver

form = SearchForm(driver)
form.set_bill_title('Agriculture Act')
form.set_session('2019-19')
form.set_current_house('Not before either House')
form.set_sort_order('Updated (oldest first)')
form.set_bill_stage('1st reading')
form.set_bill_type('Hybrid')
form.search()
print(driver.page_source)
