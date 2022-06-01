import math
from flask import Flask, render_template
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

pops = {
    "At the Border": 999_999_999,
    "Auckland": 493_990,
    "Bay of Plenty": 259_090,
    "Canterbury": 578_290,
    "Capital and Coast": 320_640,
    "Counties Manukau": 578_650,
    "Hawke's Bay": 176_110,
    "Hutt Valley": 156_790,
    "Lakes": 116_370,
    "Mid Central": 186_190,
    "Nelson Marlborough": 159_360,
    "Northland": 193_170,
    "South Canterbury": 61_955,
    "Southern": 344_900,
    "Tairāwhiti": 49_755,
    "Taranaki": 124_380,
    "Unknown": 999_999_999,
    "Waikato": 436_690,
    "Wairarapa": 48_480,
    "Waitematā": 628_770,
    "West Coast": 32_550,
    "Whanganui": 68_395
}

order = [
    "Northland",
    "Waitematā",
    "Auckland",
    "Counties Manukau",
    "Waikato",
    "Lakes",
    "Bay of Plenty",
    "Tairāwhiti",
    "Hawke's Bay",
    "Taranaki",
    "Whanganui",
    "Mid Central",
    "Wairarapa",
    "Hutt Valley",
    "Capital and Coast",
    "Nelson Marlborough",
    "West Coast",
    "Canterbury",
    "South Canterbury",
    "Southern",
    "At the Border",
    "Unknown"
]

def get_json_data():
    with open('site.html', 'r') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Extract the date of the update
    result = re.search('Last updated (.+) (\d+) (\w+) (\d+)', soup.get_text())
    _, date, month, year = result.groups()
    # print(date, month, year)

    # There are 6 tables in the page with 'table-style-two':
    # 1. Summary (new cases)
    # 2. All case outcomes since first New Zealand case (new deceased)
    # 3. Number of active cases (currently active cases)
    # 4. Source of active cases (NOT USED)
    # 5. Definitions (NOT USED)
    # 6. Total cases by location (used extensively)
    tables = soup.find_all('table', attrs={'class': 'table-style-two'})

    # total new cases
    new_cases = int(tables[0].find_all('tr')[0].td.strong.text)

    # new deceased cases
    new_deceased = int(tables[1].tbody.find_all('tr')[2].find_all('td')[0].text.strip('*'))

    # currently active cases
    active_cases = int(tables[2].tbody.find_all('tr')[0].find_all('td')[1].text)

    # new cases per location
    locations = {}
    for tr in tables[5].tbody.find_all('tr'):
        td = tr.find_all('td')
        if td[0].text == 'Total':
            continue
        locations[td[0].text] = int(td[5].text.strip('*'))
    # locations.sort(key=lambda x: x[1], reverse=True)

    return {
        'date': f"{date} {month} {year}",
        'new_cases': new_cases,
        'new_deceased': new_deceased,
        'active_cases': active_cases,
        'locations': locations
    }


@app.route("/json")
def json_endpoint():
    return get_json_data()


@app.route("/")
def hello_world():
    data = get_json_data()

    max_cases = max(data['locations'].values())

    locations = []
    for loc in data['locations'].items():
        name, cases = loc

        # IDEA: what if we considered the relative population sizes of each DHB here?
        #       how much would that realistically change the result?
        proportion = round(cases / max_cases, 4)
        symbols = ('⬜', '🟩', '🟧', '🟥')
        symbol = symbols[math.ceil(proportion * (len(symbols) - 1))]

        locations.append([name, f"{cases:,}", symbol])

    locations.sort(key=lambda x: order.index(x[0]))

    return render_template('index.html',
        date = data['date'],
        new_deceased = f"{data['new_deceased']:,}",
        new_cases = f"{data['new_cases']:,}",
        active_cases = f"{data['active_cases']:,}",
        locations = locations
    )


if __name__ == '__main__':
    app.run('0.0.0.0', debug=False)
