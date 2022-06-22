import json
import math
from flask import Flask, render_template
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

pops = {
    "Northland": 193_170,
    # "Waitematā": 628_770,
    # "Auckland": 493_990,
    "Auckland": 628_770 + 493_990 + 578_650,
    # "Counties Manukau": 578_650,
    "Waikato": 436_690,
    "Bay of Plenty": 259_090,
    "Lakes": 116_370,
    "Tair\u0101whiti": 49_755,
    "Hawke\u2019s Bay": 176_110,
    "Taranaki": 124_380,
    "Whanganui": 68_395,
    "MidCentral": 186_190,
    "Wairarapa": 48_480,
    "Hutt Valley": 156_790,
    "Capital and Coast": 320_640,
    "Nelson Marlborough": 159_360,
    "West Coast": 32_550,
    "Canterbury": 578_290,
    "South Canterbury": 61_955,
    "Southern": 344_900,
    "At the Border": 999_999_999,
    "Unknown": 999_999_999
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
    locations = []
    if len(data['cases_per_location']) != 0:
        for loc in data['cases_per_location'].items():
            name, cases = loc

            # This 'outbreak severity algorithm' is based on the log population size for each DHB
            # The constants are completely arbitrary and chosen by Histefanhere, if you don't agree with them
            # feel free to complain!
            EXPONENT_FACTOR = 1.5
            RED_CUTOFF = 25
            ORANGE_CUTOFF = 10
            GREEN_CUTOFF = 1.5

            proportion = cases / math.log(pops.get(name, 999_999_999), EXPONENT_FACTOR)

            symbol = '⬜'
            if proportion > RED_CUTOFF:
                symbol = '🟥'
            elif proportion > ORANGE_CUTOFF:
                symbol = '🟧'
            elif proportion > GREEN_CUTOFF:
                symbol = '🟩'

            # locations.append([symbol, name, f"{cases:,} . . . . . . . . . {pop_prop}"])
            locations.append([symbol, name, f"{cases:,}"])

        locations.sort(key=lambda x: order.index(x[1]))
    else:
        locations.append(["???", "???", "Locations unknown"])

    return render_template('index.html',
        **data,
        locations = locations
    )


if __name__ == '__main__':
    app.run('0.0.0.0', debug=False)
