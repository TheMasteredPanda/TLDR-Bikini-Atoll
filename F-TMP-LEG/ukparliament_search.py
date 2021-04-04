import requests
from enum import Enum
from bs4 import BeautifulSoup

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

class OriginatingHosue(Enum):
    HOC = {'value': '1', 'name': 'Hosue of Commons'}
    HOL = {'value': '2', 'name': 'House of Lords'}
    NEITHER = {'value': '3', 'name': 'Not before either House'}

'''
https://bills.parliament.uk/?SearchTerm=&Session=35&BillSortOrder=0&BillType=&BillStage=&CurrentHouse=&OriginatingHouse=&Expanded=False
'''
class StringBuilder():
    def __init__(self):
        self.url = 'https://bills.parliament.uk'
        self.bits = []

    def set_search_term(self, search_term: str):
        self.bits.append(f'SearchTerm={"+".join(search_term.split(" "))}')

    def set_session(self, session: BillSession):
        self.bits.append(f'Session={session.value["value"]}')

    def set_order(self, order: SortOrder):
        self.bits.append(f'BillSortOrder={order.value["value"]}')

    def set_bill_type(self, btype: BillType):
        self.bits.append(f'BillType={btype.value["value"]}')

    def set_current_house(self, current_house: CurrentHouse):
        self.bits.append(f'CurrentHouse={current_house.value["value"]}')

    def set_originating_house(self, originating_house: OriginatingHosue):
        self.bits.append(f'OriginatingHouse={originating_house.value["value"]}')

    def build(self):
        return f'{self.url}{"?" if len(self.bits) > 0 else ""}{"&".join(self.bits)}'

class Bill():
    def __init__(self, element: BeautifulSoup): 
        content = element.find('div', {'class': 'content'})
        self.link = content.find('a', {'class': 'overlay-link'})['href']
        self.name = content.find('div', {'class': 'primary-info'}).text
        self.session = content.find('div', {'class': 'secondary-info'}).text.replace('Session ', '').strip()
        infographic_element = content.find('div', {'class': 'infographic'})
        items = infographic_element.find_all('div', {'class': 'item-content'})
        self.originating_hosue = items[0].find('div', {'class': 'item-value'}).text
        self.next_bill_stage = items[1].find('div', {'class': 'label'}).text.replace('Next Stage: ', '')
        self.next_bill_stage_target = items[1].find('div', {'class': 'item-value'}).text.strip()
        info_element = element.find('div', {'class': 'info'})
        self.last_update = info_element.find('div', {'class': 'indicators-left'}).text.strip().replace('Last updated: ', '')
        self.bill_type = info_element.find('div', {'class': 'indicators-right'}).find('a', {'class': 'help-overlay-link'})['data-help-title']

    def get_link(self):
        return self.link

    def get_name(self):
        return self.name

    def get_session(self):
        return self.session

    def get_originating_house(self):
        return self.originating_hosue

    def get_next_bill_stage(self):
        return self.next_bill_stage

    def get_next_bill_stage_destination(self):
        return self.next_bill_stage_target

    def get_last_update(self):
        return self.last_update

    def get_bill_type(self):
        return self.bill_type
    
builder = StringBuilder()
builder.set_search_term('European Union')

print(builder.build())
soup = BeautifulSoup(response.content, features='lxml')

bill_elements = soup.find_all('div', {'class': 'card-bill'})
bills = []
next_line = '\n'

for element in bill_elements:
    bill = Bill(element)
    print('------')
    print(f'Name: {bill.get_name()}')
    print(f'Link: {bill.get_link()}')
    print(f'Session: {bill.get_session()}')
    print(f'Originating House: {bill.get_originating_house()}')
    print(f'Next Bill Stage: {bill.get_next_bill_stage()}')
    print(f'Next Bill Stage Destingation: {bill.get_next_bill_stage_destination()}')
    print(f'Last Update: {bill.get_last_update()}')
    print(f'Bill Type: {bill.get_bill_type()}')
    print('------')
    break
    #bills.append(Bill(BeautifulSoup(element))

