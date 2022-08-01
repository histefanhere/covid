import re
from bs4 import BeautifulSoup
import os
import requests
import json

def reg_extract(pattern, text):
    result = re.search(pattern, text)
    if (result):
        return result.group(1)
    else:
        return "???"

# Move execution to the location of the python script so that it saves files in the right place
os.chdir(os.path.dirname(os.path.abspath(__file__)))

x = requests.get('https://www.health.govt.nz/news-media/news-items')
# with open('site.html', 'wb') as file:
#     file.write(x.content)

soup = BeautifulSoup(x.content, 'html.parser')

articles = soup.find_all('li', class_='views-row')

for article in articles:
    # sometimes fails
    # body = article.find('span', class_='views-field-body').text
    # if "COVID-19 and vaccine update for " in body or "COVID-19 update for " in body:

    title = article.find('div', class_='views-field-title').text
    if re.search('([0-9,]+) +community cases', title) and ';' in title:

        # We've found the latest covid update article - get its URL
        # (any link in the article should go to its link)
        url = "https://www.health.govt.nz" + article.find('a')['href']

        news = requests.get(url)
        # with open('site2.html', 'wb') as file:
        #     file.write(news.content)

        news_soup = BeautifulSoup(news.content, 'html.parser')

        news_text = news_soup.find('article').text
        illegal_chars = ['\u00a0', '\u202f']
        for ill_char in illegal_chars:
            news_text = news_text.replace(ill_char, ' ')
        # print(news_text)

        # just remove astriks, much easier to deal with since they can pop up anywhere
        news_text = news_text.replace('*', '')

        out = {}

        # article link
        out['url'] = url

        # date of article
        date = news_soup.find('article').find('div', class_='field-name-field-published-date').text.strip()
        out['date'] = date

        # deaths
        out['deaths'] = reg_extract('reporting the deaths of ([0-9,]+)', news_text)
        if out['deaths'] == "???":
            title = news_soup.find('h1').text.strip()
            out['deaths'] = reg_extract('([0-9,]+) deaths', title)
        if out['deaths'] == "???":
            out['deaths'] = reg_extract('average of ([0-9,]+) deaths', news_text)

        # seven day rolling average of community cases
        out['average_cases'] = reg_extract('Seven day rolling average of community cases: ([0-9,]+)', news_text)

        # seven day rolling average of community cases from last week
        out['average_cases_previous_week'] = reg_extract('Seven day rolling average(?: of community cases)? \(as at same day last week\): ([0-9,]+)', news_text)

        # number of new cases
        out['cases'] = reg_extract('(?:Total )?[nN]umber of new community cases(?: over past .+ .+)?: ([0-9,]+)', news_text)

        # number of currently active cases
        # For some reason this does not want to work because of the no breaking space
        # out['active_cases'] = reg_extract('Number of active community cases \(total\):\u00a0([0-9,]+)', news_text)
        out['active_cases'] = reg_extract('Number of active(?: community)? cases \(total\): ([0-9,]+)', news_text)

        # cases in hospital
        out['hospitalisations'] = reg_extract('[Cc]ases in hospital: total number ([0-9,]+)', news_text)

        # cases in ICU or HDU
        out['icu'] = reg_extract('Cases in ICU or HDU: ([0-9,]+)', news_text)

        # number of new pcr tests
        out['pcr_tests'] = reg_extract('Number of PCR tests total \(last [0-9]+ hours\):? ([0-9,]+)', news_text)

        # number of new rat tests
        out['rat_tests'] = reg_extract('Number of Rapid Antigen Tests reported total \(last [0-9]+ hours\): ([0-9,]+)', news_text)

        # cases at each location
        locations = reg_extract('Location of new community cases \(PCR & RAT\)(?: over past .+ .+)?: (.+)\n', news_text).split(', ')
        out['cases_per_location'] = {}
        for location in locations:
            result = re.search('(.+) \(([0-9,]+)\)', location)
            if result:
                out['cases_per_location'][result.group(1).replace('*', '')] = int(result.group(2).replace(',', ''))

        # If extracting locations from the news update doesn't work, get it from the table
        if not out['cases_per_location']:
            x = requests.get("https://www.health.govt.nz/covid-19-novel-coronavirus/covid-19-data-and-statistics/covid-19-current-cases")
            soup = BeautifulSoup(x.content, 'html.parser')

            tables = soup.find_all('table', attrs={'class': 'table-style-two'})

            # new cases per location
            locations = {}
            for tr in tables[5].tbody.find_all('tr'):
                td = tr.find_all('td')
                if td[0].text == 'Total':
                    continue
                locations[td[0].text.strip('*')] = int(td[5].text.strip('*'))

            # combine auckland with Waitematā and Counties Manukau
            locations['Auckland'] = locations['Auckland'] + locations['Waitematā'] + locations['Counties Manukau']
            del locations['Waitematā']
            del locations['Counties Manukau']

            # fix locations to be consistent
            locations["Hawke\u2019s Bay"] = locations.pop('Hawke\'s Bay')
            locations["MidCentral"] = locations.pop('Mid Central')

            out['cases_per_location'] = locations

        print(out)

        with open('data.json', 'w+') as file:
            json.dump(out, file, indent=4)

        break
