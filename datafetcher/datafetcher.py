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

input_file_name = os.path.join(repo_path, 'data', 'OxCGRT_latest.csv')
with open(input_file_name, 'r') as csvfile:
    print('Reading {}'.format(input_file_name))
    reader = csv.DictReader(csvfile)

    for row in reader:
        country_name = row['CountryName']
        
        country_code_3 = row['CountryCode']
        country_code = None
        if country_code_3 in country_code_3_to_2:
            country_code = country_code_3_to_2[country_code_3]
        else:
            print('Cannot convert country code {}.'.format(country_code_3))
            continue

        stringency_index = None
        try:
            stringency_index = float(row['StringencyIndex'])
        except ValueError:
            pass
        entry_date = datetime.strptime(row['Date'], '%Y%m%d').strftime('%Y-%m-%d')

        if country_code not in country_data:
            if stringency_index is not None and stringency_index > 0:
                country_data[country_code] = { 
                    'country_name' : country_name,
                    'lockdown_date' : entry_date,
                    'stringency_index' : stringency_index,
                }
        else:
            if stringency_index is not None:
                country_data[country_code]['stringency_index'] = stringency_index

    country_data = dict(filter(lambda item: item[1]['stringency_index'] > 0, country_data.items()))

output_file_name = os.path.join(script_path, os.pardir, 'countrydata.js')
print('Writing {}'.format(output_file_name))
with open(output_file_name, 'w') as outfile:
    outfile.write('const countryData=');
    json.dump(country_data, outfile, separators=(',', ':'))
    outfile.write(';');
