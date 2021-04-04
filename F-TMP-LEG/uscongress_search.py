from enum import Enum
import time
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select

options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)
driver.get('https://www.govtrack.us/congress/bills/browse')

class Choice():
    def __init__(self, element: WebElement):
        self.input = element.find_element_by_tag_name('input')
        self.label: WebElement = element.find_element_by_tag_name('label')
        name_element = self.label.find_element_by_class_name('name')
        self.name = name_element.get_attribute('innerHTML')
        count_element = self.label.find_element_by_class_name('count')
        self.count = count_element.get_attribute('innerHTML').replace('(', '').replace(')', '')

    def get_name(self):
        return self.name

    def get_count(self):
        return self.count

    def get_input(self):
        return self.input

    def click(self):
        self.input.click()

class CongressOption():
    def __init__(self, element: WebElement):
        self.value = element.get_attribute('value')
        inner_html = element.get_attribute('innerHTML')
        if self.value != '__ALL__':
            split_ih = inner_html.split(': ')
            self.congress = split_ih[0]
            start_to_end_year = split_ih[1][0:8]
            split_years = start_to_end_year.split('-')
            self.start_year = split_years[0]
            self.end_year = split_years[1]
            self.bills = split_ih.replace(start_to_end_year, '').strip().replace('(', '').replace(')', '').replace('bills', '')

    def check_value(self):
        if self.value == '__ALL__':
            raise Exception('Value is __ALL__')

    def get_congress_meeting(self):
        self.check_value()
        return self.congress

    def get_start_year(self):
        self.check_value()
        return self.start_year

    def get_end_year(self):
        self.check_value()
        return self.end_year

    def get_bills(self):
        self.check_value()
        return self.bills

    def get_value(self):
        return self.value

class CommiteeOption():
    def __init__(self, element: WebElement):
        self.option = element
        self.value = element.get_attribute('value')
        inner_html = element.get_attribute('innerHTML')
        open_bracket_position = inner_html.find('(')
        self.name = inner_html[0:open_bracket_position-1]
        self.bills = inner_html[open_bracket_position-1:None]
    
    def check_value(self):
        if self.value == '__ALL__':
            raise Exception('Value is __ALL__')

    def get_option(self):
        self.check_value()
        return self.option

    def get_value(self):
        self.check_value()
        return self.value

    def get_name(self):
        self.check_value()
        return self.name

    def get_bills_introducted(self):
        self.check_value()
        return self.bills

'''
Class used to interact with the search form on govtrack.us/congress/bills/browse.

Unlike the bills search form this search form is interactive.
'''
class SearchForm():
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.search_box_element: WebElement = driver.find_element_by_id('searchform_field_text')
        self.search_button = driver.find_element_by_id('searchform_field_text_button')
        self.congress_option_element: Select = driver.find_element_by_id('searchform_field_congress')

        congress_meetings = {}

        for option in self.congress_option_element.options:
            entry = CongressOption(option)
            congress_meetings[entry.get_value()] = entry

        self.meetings = congress_meetings
        self.sponsor_option_element = driver.find_element_by_id('searchform_field_sponsor')
        current_status_checkboxes: WebElement = driver.find_element_by_id('searchform_field_current_status')

        status_checkboxes = {}

        for element in current_status_checkboxes.find_elements_by_class_name('choices'): 
            choice = Choice(element)
            status_checkboxes[choice.get_name().lower()] = choice
        self.bill_status_choices = status_checkboxes

        enacted_container = driver.find_element_by_id('searchform_field_enacted_ex_container')
        self.enacted_option = enacted_container.find_element_by_id('searchform_field_enacted_ex')
        self.enacted_title = self.enacted_option.get_attribute('innerHTML')
        enacted_count_element = enacted_container.find_element_by_class_name('count')
        self.enacted_count = enacted_count_element.get_attribute('innerHTML')
        self.cosponsor_option = driver.find_element_by_id('searchform_field_cosponsor')

        self.committee_option: Select = driver.find_element_by_id('searchform_field_committees')

        committee_options = []

        for option in self.committee_option.options:
            committee_options.append(CommiteeOption(option))

        self.committee_options = committee_options

        self.bill_subject_option: Select = driver.find_element_by_id('searchform_field_terms')

        subjects = {}

        for option in self.bill_subject_option.options:
            subjects[option.get_attribute('value')] = option.get_attribute('innerHTML')

        self.bill_subjects = subjects
        self.party_sponsor_option = driver.find_element_by_id('searchform_field_sponsor_party')
        bill_type_element = driver.find_element_by_id('searchform_field_bill_type')
        bill_type_choices = []
        
        for element in bill_type_element.find_elements_by_class_name('choices'):
            bill_type_choices.append(Choice(element))
        
        self.bill_type_choices = bill_type_choices

    def set_search_box_content(self, content: str):
        self.search_box_element.clear()
        self.search_box_element.send_keys(content)

    def get_congress_meetings(self):
        return self.meetings

    def set_congress_option(self, value: str):
        self.congress_option_element.select_by_value(value)

    def get_status_choices(self):
        return self.bill_status_choices

    def get_enacted_choice(self):
        return self.enacted_option

    def get_enacted_count(self):
        return self.enacted_count

    def get_enacted_title(self):
        return self.enacted_title

    def get_committee_options(self):
        return self.committee_options
    
    def set_committee(self, value: str):
        self.committee_option.select_by_value(value)

    def get_bill_subjects(self):
        return self.bill_subjects

    def set_bill_subject(self, value: str):
        self.bill_subject_option.select_by_value(value)

    def set_cosponsor(self, value: str):
        self.cosponsor_option.select_by_value(value)

    def set_party_sponsor(self, value: str):
        self.party_sponsor_option.select_by_value(value)
    
    def get_bill_type_choices(self):
        return self.bill_type_choices

class BillType(Enum):
    ALL = {'value': 'All', 'name': 'All Bills'}
    HB = {'value': 'H.R.', 'name': 'House Bill'}
    SB = {'value': 'S.', 'name': 'Senate Bill'}
    HRES = {'value': 'H.Res.', 'name': 'House Resolution'}
    SRES = {'value': 'S.Res', 'name': 'Senate Resolution'}
    HJRES = {'value': 'H.J.Res.', 'name': 'Joint Resolution Originating in House of Respresentatives'}
    SJRES = {'value': 'S.J.Res.', 'name': 'Join Resolution Originating in Senate'}
    HCRES = {'value': 'H.Con.Res.', 'name': 'Concurrent Resolution Originating in House of Respresentatives'}
    SCRES = {'value': 'S.Con.Res.', 'name': 'Concurrent Resolution Originating in Senate'}

    @classmethod
    def from_name(cls, name: str):
        for btype in cls:
            if name.upper() == btype.name:
                return name
        raise Exception(f'{name} is not a valid enum')

    @classmethod
    def from_value(cls, value: str):
        for btype in cls:
            if value.lower() == btype.value['value'].lower():
                return btype
        raise Exception(f'{value} is not a value associated with any of the enums')

    @classmethod
    def is_valid(cls, name: str):
        try:
            cls.from_name(name)
            return True
        except Exception as ignore:
            return False

class Bill():
    def __init__(self, element: WebElement):
        divs = element.find_elements_by_tag_name('div')
        information_container = divs[1]
        information_container_divs = information_container.find_elements_by_tag_name('div')
        title_content = information_container_divs[0].find_element_by_tag_name('a').get_attribute('innerHTML')
        split_title = title_content.split(':')
        self.title = split_title[1].strip()
        bill_id_split = split_title[0].strip().split(' ')
        self.bill_id = bill_id_split[1]
        self.bill_type = BillType.from_value(bill_id_split[0])
        table_elements = information_container_divs[1].find_element_by_tag_name('table').find_elements_by_tag_name('td')
        self.introduced = table_elements[0].get_attribute('innerHTML').split('<br>')[1]
        stage_element = table_elements[1]
        stage_element_content = stage_element.get_attribute('innerHTML').split('<br>')
        self.current_stage = stage_element_content[0]
        self.current_stage_date = stage_element_content[1]
        cosponsor_element_content = table_elements[2].get_attribute('innerHTML').split('<br>')
        cosponsor_split = cosponsor_element_content[1].strip().split(' ')
        self.cosponsor_count = cosponsor_split[0]
        self.cosponsor_constitution = cosponsor_split[1].replace('(', '').replace(')', '').split(',')
        progression = None
        if len(table_elements) == 4:
            content = table_elements[3].get_attribute('innerHTML')
            if content == '' or content is None: return
            progression = content.split('<br>')[1]
        self.progression = progression

    def get_title(self):
        return self.title

    def get_bill_id(self):
        return self.bill_id

    def get_bill_type(self):
        return self.bill_type

    def get_introduction_date(self):
        return self.introduced

    def get_current_stage(self):
        return self.current_stage

    def get_cosponsor_count(self):
        return self.cosponsor_count

    def get_consponsor_constitution(self):
        return self.cosponsor_constitution

    def get_progression(self):
        try:
            return self.progression
        except AttributeError as ignore:
            return None


time.sleep(2)
results_element = driver.find_element_by_class_name('results')
bills = results_element.find_elements_by_class_name('row')

for entry in bills:
    bill = Bill(entry)
    """divs = entry.find_elements_by_tag_name('div')
    image_container = divs[0]
    img_element = image_container.find_element_by_tag_name('img')
    information_container = divs[1]
    information_container_divs = information_container.find_elements_by_tag_name('div')
    title_container = information_container_divs[0]
    title_element = title_container.find_element_by_tag_name('a')
    title = title_element.get_attribute('innerHTML')
    table_container = information_container_divs[1]
    table_element = table_container.find_element_by_tag_name('table')
    table_elements = table_element.find_elements_by_tag_name('td')
    """
    print('-----------------------------------------------------')
    next_line = '\n'
    print(f'Title: {bill.get_title()}{next_line}Introduced: {bill.get_introduction_date()}{next_line}Current Stage: {bill.get_current_stage()}{next_line}Cosponsor Count: {bill.get_cosponsor_count()}{next_line}Cosponsor Consitution: {bill.get_consponsor_constitution()}{next_line}Bill ID: {bill.get_bill_id()}{next_line}Bill Type: {bill.get_bill_type().name}')
    print(f'Progression: {bill.get_progression()}' if bill.get_progression() is not None else '')
    """
    print(f'Title: {title}')

    for table_entry in table_elements:
        table_content = table_entry.get_attribute('innerHTML')
        split_table_content = table_content.split('<br>')
        print(f'{split_table_content[0]}: {split_table_content[1] if len(split_table_content) > 1 else ""}')
    """
    print('-----------------------------------------------------')
