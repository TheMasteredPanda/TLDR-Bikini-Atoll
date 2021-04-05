from os import name
from bs4 import BeautifulSoup
from enum import Enum
import selenium
from selenium.webdriver import Chrome, ChromeOptions
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By

class CongressOption():
    def __init__(self, element: WebElement):
        self.value = element.get_attribute('value')
        inner_html = element.get_attribute('innerHTML').split(': ')[1].split(' ')
        self.session_length = inner_html[0]
        self.bills_introduced = inner_html[1].replace('(', '').replace(')', '').replace('bills', '').strip()

    def get_value(self):
        return self.value

    def get_session_length(self):
        return self.session_length

    def get_bills_introduced(self):
        return self.bills_introduced

class CurrentStatusCheckbox():
    def __init__(self, element: WebElement):
        input_element = element.find_element_by_tag_name('input')
        self.value = input_element.get_attribute('value')
        label_element = element.find_element_by_class_name('name')
        self.name = label_element.get_attribute('innerHTML')
        if self.name != 'All':
            count_element = element.find_element_by_class_name('count')
            self.count = count_element.get_attribute('innerHTML').replace('(', '').replace(')', '').replace('bills', '')

    def get_value(self):
        return self.value

    def get_name(self):
        return self.name

    def get_count(self):
        if self.name == 'All':
            return '0'
        else:
            return self.count

class CommitteeOption():
    def __init__(self, element: WebElement):
        self.value = element.get_attribute('value')
        inner_html = element.get_attribute('innerHTML').split(' (')
        self.name = inner_html[0].strip()
        self.bills_introduced = inner_html[1].replace(')', '').replace('bills', '')

    def get_value(self):
        return self.value

    def get_name(self):
        return self.name

    def get_bills_introduced(self):
        return self.bills_introduced

class PartyMember():
    def __init__(self, element: WebElement):
        self.value = element.get_attribute('value')
        inner_html = element.get_attribute('innerHTML')
        member_type = 'Representative'
        split_value = '(Rep.)'

        if '(Rep.)' not in inner_html:
            member_type = 'Senator'
            split_value = '(Sen.)'
        
        if '(Commish.)' in inner_html:
            member_type = 'Commissioner'
            split_value = '(Commish.)'

        self.member_type = member_type
        inner_html_split = inner_html.split(split_value)
        self.member_name = inner_html_split[0].strip()
        inner_html_split_2 = inner_html_split[1].split(' (')
        representing = inner_html_split_2[0].strip().replace(']', '').replace('[', '')
        self.party_key = representing[0]
        self.representing = representing.replace(f'{self.party_key}-', '')
        self.cosponsor_bills = inner_html_split_2[1].replace(')', '').replace('bills', '').strip()
        self.sponsored_bills = "0"

    def get_value(self):
        return self.value

    def get_member_type(self):
        return self.member_type
    
    def get_representing_area(self):
        return self.representing

    def get_key(self):
        return self.party_key

    def get_bills_cosponsored(self):
        return self.cosponsor_bills

    def get_bills_sponsored(self):
        return self.sponsored_bills

    def set_bills_sponsored(self, value: str):
        self.sponsored_bills = value

class Party():
    def __init__(self, element: WebElement):
        self.value = element.get_attribute('value')
        inner_html = element.get_attribute('innerHTML').split(' (')
        self.bills = inner_html[1].replace(')', '').replace('bills', '')
        self.members = []

    def get_name(self):
        return self.value

    def get_value(self):
        return self.value.replace(' ', '+')

    def get_bills(self):
        return self.bills

    def get_key(self):
        return self.value[0]

    def add_member(self, member: PartyMember):
        self.members.append(member)
    
    def find_member_by_id(self, value: str):
        for member in self.members:
            if member.get_value() == value:
                return member

    def find_member_by_area(self, value: str):
        for member in self.members:
            if member.get_representing_area().lower() == value.lower():
                return member

class BillType(Enum):
    ALL = {'value': 'All', 'name': 'All Bills'}
    HB = {'value': 'H.R.', 'name': 'House Bill'}
    SB = {'value': 'S.', 'name': 'Senate Bill'}
    HRES = {'value': 'H.Res.', 'name': 'House Resolution'}
    SRES = {'value': 'S.Res.', 'name': 'Senate Resolution'}
    HJRES = {'value': 'H.J.Res.', 'name': 'Joint Resolution Originating in House of Respresentatives'}
    SJRES = {'value': 'S.J.Res.', 'name': 'Join Resolution Originating in Senate'}
    HCRES = {'value': 'H.Con.Res.', 'name': 'Concurrent Resolution Originating in House of Respresentatives'}
    SCRES = {'value': 'S.Con.Res.', 'name': 'Concurrent Resolution Originating in Senate'}
    
    @classmethod
    def from_name(cls, name: str):
        for option in cls:
            if option.name.lower() == name.lower():
                return option
        raise Exception(f'{name} is not a valid enum')

    @classmethod
    def from_value(cls, value: str):
        for option in cls:
            if option.value['value'].lower() == value.lower():
                return option
        raise Exception(f'{value} is no associated with any enum')

    @classmethod
    def is_valid(cls, name: str):
        try:
            cls.from_name(name)
            return True
        except Exception as ignore:
            try:
                cls.from_value(name)
                return True
            except Exception as ignore_2:
                return False
            return False


class BillTypeCheckbox():
    def __init__(self, element: WebElement):
        self.value = element.find_element_by_tag_name('input').get_attribute('value')
        self.bill_type = BillType.from_value(element.find_element_by_class_name('name').get_attribute('innerHTML'))
        self.count = element.find_element_by_class_name('count').get_attribute('innerHTML').replace('(', '').replace(')', '').replace('bills', '')

    def get_value(self):
        return self.value

    def get_type(self):
        return self.bill_type

    def get_bill_count(self):
        return self.count

class DataParser():
    def __init__(self):
        options = ChromeOptions()
        options.headless = True
        self.driver = Chrome(options=options)
        self.driver_wait = WebDriverWait(self.driver, 20)
        self.driver.get('https://www.govtrack.us/congress/bills/browse')
        self.bills = []
        self.congress_options = []
        self.current_status_choices = []
        self.committee_options = []
        self.subjects = []
        self.parties = []
        self.bill_choices = []
        self.all_option = {'value': '__ALL__', 'name': 'All'}
        
    def parse_select_options(self):
        try:
            self.driver_wait.until(EC.presence_of_element_located((By.ID, 'searchform')))
            field_congress_select = Select(self.driver_wait.until(EC.presence_of_element_located((By.ID, 'searchform_field_congress'))))
            field_current_status: WebElement = self.driver_wait.until(EC.presence_of_element_located((By.ID, 'searchform_field_current_status')))
            current_status_choices = field_current_status.find_elements_by_class_name('choices')
            field_comittees = Select(self.driver_wait.until(EC.presence_of_element_located((By.ID, 'searchform_field_committees'))))
            self.driver_wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#searchform_field_committees>option')))
            print('Found committee options')
            field_terms = Select(self.driver_wait.until(EC.presence_of_element_located((By.ID, 'searchform_field_terms'))))
            self.driver_wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#searchform_field_terms>option')))
            field_sponsor_party = Select(self.driver_wait.until(EC.presence_of_element_located((By.ID, 'searchform_field_sponsor_party'))))
            field_cosponsors = Select(self.driver_wait.until(EC.presence_of_element_located((By.ID, 'searchform_field_cosponsors'))))
            self.driver_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#searchform_field_cosponsors>option')))
            field_sponsors = Select(self.driver_wait.until(EC.presence_of_element_located((By.ID, 'searchform_field_sponsor'))))
            field_bill_type: WebElement = self.driver_wait.until(EC.presence_of_element_located((By.ID, 'searchform_field_bill_type')))
            field_bill_type_choices = field_bill_type.find_elements_by_class_name('choices')
            field_bill_type_choices.pop(0)
            
            print('Indexing bill type checkboxes...')
            for choice in field_bill_type_choices:
                self.bill_choices.append(BillTypeCheckbox(choice))

            print('Indexing parties...')
            for option in field_sponsor_party.options:
                if option.get_attribute('value') == '__ALL__': continue
                self.parties.append(Party(option))

            print('Indexing cosponsors...')
            for option in field_cosponsors.options:
                if option.get_attribute('value') == '__ALL__': continue
                member = PartyMember(option)
                self.get_party_by_key(member.get_key()).add_member(member)

            democrat_party = self.get_party_by_key('D')
            republican_party = self.get_party_by_key('R')
            independent_party = self.get_party_by_key('I')

            for option in field_sponsors.options:
                inner_html = option.get_attribute('innerHTML')
                split_value = '(Rep.)'
                value = option.get_attribute('value')
                if value == '__ALL__': continue
                if '(Sen.)' in inner_html:
                    split_value = '(Sen.)'

                if '(Commish.)' in inner_html:
                    split_value = '(Commish.)'

                split_inner_html = inner_html.split(split_value)
                section = split_inner_html[1].strip()
                split_section = section.split(' (')
                bills = split_section[1].replace(')', ')').replace('bills', '')

                if 'D-' in split_section[0]:
                    democrat_party.find_member_by_id(value).set_bills_sponsored(bills)
                
                if 'R-' in split_section[0]:
                    republican_party.find_member_by_id(value).set_bills_sponsored(bills)

                if 'I-' in split_section[0]:
                    independent_party.find_member_by_id(value).set_bills_sponsored(bills)
                    

            print('Indexing subjects...')
            for option in field_terms.options:
                self.subjects.append({'value': option.get_attribute('value'), 'name': option.get_attribute('innerHTML')})

            print('Indexing commitee options...')
            for option in field_comittees.options:
                if option.get_attribute('value') == '__ALL__': continue
                self.committee_options.append(CommitteeOption(option))

            print('Indexing status choices...')
            for choice in current_status_choices:
                self.current_status_choices.append(CurrentStatusCheckbox(choice))

            print('Indexing congress meetings...')
            for option in field_congress_select.options:
                if option.get_attribute('value') == '__ALL__': continue
                self.congress_options.append(CongressOption(option))

            exit()
        except TimeoutException as ignore:
            print('Timeout 0')
            self.driver.quit()
            exit()
        

    def get_party_by_key(self, key: str):
        for party in self.parties:
            if key.lower() == party.get_key().lower():
                return party

    def remove_followus_modal(self):
        try:
            followus_modal = self.driver_wait.until(EC.visibility_of_element_located((By.ID, 'followus_modal')))
            modal_dialogue = self.driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'modal-dialog')))
            followus_modal.find_element_by_class_name('btn-default').click()
        except TimeoutException as ignore:
            print('Timeout 2')
            self.driver.quit()
            exit()

    def parse(self):

        try:
            self.driver_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.result_item')))
            
            soup = BeautifulSoup(self.driver.page_source)
            results_element = soup.find('div', {'class', 'results'})
            bill_rows = results_element.find_all('div', {'class', 'row'})
            #print(bill_rows[0].prettify())

            for row in bill_rows:
                self.bills.append(Bill(row))

        except TimeoutException as ignore:
            print('Timeout')
            self.driver.quit()
            exit()


    def get_bills(self):
        return self.bills

class Bill():
    def __init__(self, element):
        divs = element.find_all('div')
        outer_name_container = divs[1]
        name_container = outer_name_container.find('div')
        name_element = name_container.find('a')
        self.link = name_element['href']
        bill_full_name = name_element.text
        split_bill_name = bill_full_name.split(': ')
        self.name = split_bill_name[1]
        bill_split_type_in_name = split_bill_name[0].split(' ')
        self.bill_id = bill_split_type_in_name[1]
        self.type = bill_split_type_in_name[0]
        info_container = divs[3]
        sponsor_container = info_container.find('div')
        self.sponsor = sponsor_container.text.replace('Sponsor: ', '')
        table_element = info_container.find('table')
        td_elements = table_element.find_all('td')
        self.introduced = td_elements[0].text.replace('Introduced: ', '')
        full_current_state = td_elements[1].decode_contents().split('<br/>')
        self.current_state_name = full_current_state[0]
        self.current_state_date = full_current_state[1]
        cosponsors_element = td_elements[2].decode_contents().split('<br/>')
        cosponsor_text_split = cosponsors_element[1].split(' ')
        self.cosponsors_count = cosponsor_text_split[0]
        self.cosponsors_constition = cosponsor_text_split[1].replace('(', '').replace(')', '').split(',')
        if len(td_elements) > 4:
            self.progress = td_elements[3].decode_contents().split('<br/>')[1]

    def get_bill_title(self):
        return self.name

    def get_bill_id(self):
        return self.bill_id

    def get_bill_type(self):
        return self.type

    def get_sponsor(self):
        return self.sponsor

    def get_current_state_name(self):
        return self.current_state_name

    def get_cosponsors_count(self):
        return self.cosponsors_count

    def get_cosponsors_constitution(self):
        return self.cosponsors_constition

    def get_link(self):
        return self.link


'''
https://www.govtrack.us/congress/bills/browse#
    text=public+safety
    &congress=116
    &sponsor=412607
    &cosponsors=412625
    &committees=2668
    &terms=5816
    &sponsor_party=Democrat
    &bill_type[]=5,4
    $current_status[]=4,4
'''
parse = DataParser()
parse.remove_followus_modal()
parse.parse_select_options()
parse.parse()

for bill in parse.get_bills():
    print('-----')
    next_line = '\n'
    print(f"Title: {bill.get_bill_title()}{next_line}Bill ID: {bill.get_bill_id()}{next_line}Bill Type: {bill.get_bill_type()}{next_line}Bill Link: {bill.get_link()}{next_line}Sponsor: {bill.get_sponsor()}{next_line}Cosponsor Count: {bill.cosponsors_count}{next_line}Cosponsor Constitution: {bill.get_cosponsors_constitution()}")
    print('-----')
