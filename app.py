import json
import math
from flask import Flask, render_template
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

# Not currently in use
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
    # "Waitematā",
    "Auckland",
    # "Counties Manukau",
    "Waikato",
    "Bay of Plenty",
    "Lakes",
    "Tair\u0101whiti",
    "Hawke\u2019s Bay",
    "Taranaki",
    "Whanganui",
    "MidCentral",
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


@app.route("/")
def hello_world():
    try:
        with open('data.json', 'rb') as file:
            data = json.load(file)
    except OSError:
        return "<p>Failed to read data.json file</p>"

    # This part is dedicated to calculating and outputting the coloured squares next to each location
    max_cases = max(data['cases_per_location'].values())
    locations = []
    for loc in data['cases_per_location'].items():
        name, cases = loc

        # IDEA: what if we considered the relative population sizes of each DHB here?
        #       how much would that realistically change the result?
        proportion = round(cases / max_cases, 4)
        symbols = ('⬜', '🟩', '🟧', '🟥')
        symbol = symbols[math.ceil(proportion * (len(symbols) - 1))]

        locations.append([name, f"{cases:,}", symbol])

    locations.sort(key=lambda x: order.index(x[0]))

    return render_template('index.html',
        **data,
        locations = locations
    )


if __name__ == '__main__':
    app.run('0.0.0.0', debug=False)
