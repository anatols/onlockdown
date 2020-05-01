#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import os
import csv
import json
from datetime import datetime
from countrycodes import country_code_3_to_2

script_path = os.path.dirname(os.path.realpath(__file__))

repo_uri = 'git@github.com:OxCGRT/covid-policy-tracker.git'
repo_path = os.path.join(script_path, 'covid-policy-tracker')

os.chdir(script_path)
if not os.path.exists(repo_path):
    subprocess.call(['git', 'clone', repo_uri])

os.chdir(repo_path)
subprocess.call(['git', 'checkout', '-f', 'master'])
subprocess.call(['git', 'pull'])
os.chdir(script_path)

country_data = {}

lockdown_indicators = [
    'C1_School closing',
    'C2_Workplace closing',
    'C5_Close public transport',
    'C6_Stay at home requirements',
    'C7_Restrictions on internal movement',
]

input_file_name = os.path.join(repo_path, 'data', 'OxCGRT_latest.csv')
with open(input_file_name, 'r') as csvfile:
    print('Reading {}'.format(input_file_name))
    reader = csv.DictReader(csvfile)

    last_known_indicators_per_country = {}

    for row in reader:
        country_name = row['CountryName']
        
        country_code_3 = row['CountryCode']
        country_code = None
        if country_code_3 in country_code_3_to_2:
            country_code = country_code_3_to_2[country_code_3]
        else:
            print('Cannot convert country code {}.'.format(country_code_3))
            continue

        if country_code not in last_known_indicators_per_country:
            last_known_indicators_per_country[country_code] = {}
            for indicator_name in lockdown_indicators:
                last_known_indicators_per_country[country_code][indicator_name] = 0.0

        for indicator_name in lockdown_indicators:
            indicator_value = None
            try:
                indicator_value = float(row[indicator_name])
            except ValueError:
                pass

            if indicator_value is not None:
                last_known_indicators_per_country[country_code][indicator_name] = indicator_value

        locked_down = False
        for indicator_name in lockdown_indicators:
            if last_known_indicators_per_country[country_code][indicator_name] >= 2.0:
                locked_down = True

        entry_date = datetime.strptime(row['Date'], '%Y%m%d').strftime('%Y-%m-%d')

        if country_code not in country_data:
            country_data[country_code] = { 
                'name' : country_name
            }

        if locked_down:
            if 'start' not in country_data[country_code]:
                country_data[country_code]['start'] = entry_date
        else:
            if 'start' in country_data[country_code]:
                country_data[country_code]['end'] = entry_date

output_file_name = os.path.join(script_path, os.pardir, 'countrydata.js')
print('Writing {}'.format(output_file_name))
with open(output_file_name, 'w') as outfile:
    outfile.write('const countryData=');
    json.dump(country_data, outfile, separators=(',', ':'))
    outfile.write(';');
