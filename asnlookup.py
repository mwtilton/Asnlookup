#!/usr/bin/python

import csv
import sys
import argparse
import requests
# import re
import os
import json

from time import sleep
from termcolor import colored
# from bs4 import BeautifulSoup
from zipfile import ZipFile

requests.packages.urllib3.disable_warnings()

def banner():
        print('''
        ____ ____ _  _ _    ____ ____ _  _ _  _ ___
        |__| [__  |\ | |    |  | |  | |_/  |  | |__]
        |  | ___] | \| |___ |__| |__| | \_ |__| |

Author: mwtilton
Version: 1.0.2
        ''')

def parse_args():
    # parse the argument
    parser = argparse.ArgumentParser(epilog='\tExample: \r\npython ' + sys.argv[0] + " -o twitter -l <license key>")
    org = parser.add_argument('-o', '--org', help="Organization to look up", required=True)
    license = parser.add_argument('-l', '--license', help="License to use for maxmind.", required=True)
    output = parser.add_argument('--output', help="Output path (optional)", required=False, default=None)
    return parser.parse_args()

def check_licensekey(license_key):
    if not license_key:
        print (colored('[!] Please enter a valid Maxmind user license key in config.py.', 'red'))
        sys.exit(1)
    else:
        try:
            r = requests.head('{}'.format(download_link))
            if r.status_code == requests.codes.ok:
                print (colored("[*] User's license key is valid!\n", 'green'))
            else:
                print (colored("[!] Please enter a valid Maxmind user license key in config.py.", 'red'))
                sys.exit(1)
        except requests.exceptions.RequestException as e:
            print (e)
            sys.exit(1)

def download_db(download_link, output_path):
    
    geolite_asn_zip_filepath = f'{output_path}/GeoLite2-ASN-CSV.zip'
    geolite_asn_ipv4_csv_filepath = f'{output_path}/GeoLite2-ASN-Blocks-IPv4.csv'

    # Download a local copy of ASN database from maxmind.com
    if (os.path.isfile(geolite_asn_ipv4_csv_filepath)) == False:
        print(colored("[*] Downloading ASN database ...\n", "red"))
        os.system(f"wget -O {geolite_asn_zip_filepath} '{download_link}'")
        
        with ZipFile(geolite_asn_zip_filepath, 'r') as zip_ref:
            zip_ref.extractall(f'{output_path}')
        
        os.system(f"mv {output_path}/Geo*/GeoLite2-ASN-Blocks-IPv4.csv {geolite_asn_ipv4_csv_filepath}")
        
        print(colored("\nDone!\n", "red"))

def extract_asn(organization, output_path):
    #read csv, and split on "," the line
    asn_ipv4 = csv.reader(open(f'{output_path}/GeoLite2-ASN-Blocks-IPv4.csv', "r"), delimiter=",")
    output = {}

    #loop through ASN blocks list
    for row in asn_ipv4:
        #if current rows 2nd value is equal to input, print that row
        if organization.upper().replace('_', ' ') in row[2].upper():
            output.update({row[1] : row[2]})
    
    return(output)

def extract_ip(asn):

    ipinfo = f"https://api.bgpview.io/asn/AS{asn}/prefixes"
    
    try:
        response = requests.get(ipinfo, headers={'accept': 'application/json'})
    except:
        print(colored("[*] Timed out while trying to the ASN lookup server, please run the tool again.", "red"))
        sys.exit(1)
    
    # Requires Rest between API calls, otherwise it will return none
    sleep(1)
    jsondata = response.json()
    
    ipv4 = {}
    
    for cidr in jsondata['data']['ipv4_prefixes']:
        ipv4.update({cidr['prefix']:cidr['description']})
    
    return(ipv4)

if __name__ == '__main__':
    banner()
    org = (parse_args().org).replace(' ', '_')
    license_key = parse_args().license
    
    if parse_args().output is None:
        output_path = os.path.join(f'/tmp/{org}', 'output')
    else:
        output_path = os.path.join(parse_args().output, f'{org}/output')

    if (os.path.exists(f'{output_path}') == False):
        os.makedirs(f'{output_path}')

    print(f"ASN Output Path: {output_path}")
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # useragent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:64.0) Gecko/20100101 Firefox/64.0'
    # download_link = 'https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-ASN-CSV&license_key={}&suffix=zip'.format(license_key)
    download_link = f'https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-ASN-CSV&license_key={license_key}&suffix=zip'

    print(f"Checking License Key...")
    check_licensekey(license_key)
    
    download_db(license_key, output_path)

    extracted_asn_output = extract_asn(org, output_path)
    with open(f'{output_path}/extracted_asn_output.json', 'w') as json_file:
        json.dump(extracted_asn_output, json_file)

    extracted_ip_output = {}
    for key, value in extracted_asn_output.items():
        print(colored(f"{key}: {value}", "blue"))
        extracted_ip_output.update({key:extract_ip(key)})
    
    print(colored(f"[*] IP addresses owned by {org} are the following:","green"))
    print(json.dumps(extracted_ip_output, sort_keys=True, indent=4))

    with open(f'{output_path}/extracted_ip_output.json', 'w') as json_file:
        json.dump(extracted_ip_output, json_file)

    print(colored(f"[*] DeDupe IP addresses owned by {org} are the following:","green"))

    dedupeipaddresses = {}
    count = 0
    for key, value in extracted_ip_output.items():
        count += len(value)
        for ky, val in value.items():
            dedupeipaddresses.update({ky:''})
    
    with open(f'{output_path}/dedupe_ip_addresses.json', 'w') as json_file:
        json.dump(extracted_ip_output, json_file)
    print(json.dumps(extracted_ip_output, sort_keys=True, indent=4))
    
    print(colored(f"[+] {org} ASN search is completed.","cyan"))