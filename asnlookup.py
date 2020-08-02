#!/usr/bin/python

import csv
import sys
import argparse
import requests
import re
import os
from termcolor import colored
from bs4 import BeautifulSoup
requests.packages.urllib3.disable_warnings()

def banner():
        print('''
        ____ ____ _  _ _    ____ ____ _  _ _  _ ___
        |__| [__  |\ | |    |  | |  | |_/  |  | |__]
        |  | ___] | \| |___ |__| |__| | \_ |__| |
        ''')

def parse_args():
    # parse the argument
    parser = argparse.ArgumentParser(epilog='\tExample: \r\npython ' + sys.argv[0] + " -o twitter")
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

def download_db(download_link, org, useragent):
    geolite_asn_zip_filepath = f'/tmp/{org}/GeoLite2-ASN-CSV.zip'
    geolite_asn_filesize_filepath = f'/tmp/{org}/filesize.txt'
    
    geolite_asn_ipv4_csv_filepath = f'/tmp/{org}/GeoLite2-ASN-Blocks-IPv4.csv'
    geolite_asn_ipv6_csv_filepath = f'/tmp/{org}/GeoLite2-ASN-Blocks-IPv6.csv'

    if (os.path.exists(f'/tmp/{org}') == False):
        os.makedirs(f'/tmp/{org}')

    # Download a local copy of ASN database from maxmind.com
    if (os.path.isfile(geolite_asn_ipv4_csv_filepath)) == False:
        print(colored("[*] Downloading ASN database ...\n", "red"))
        os.system(f"wget -O {geolite_asn_zip_filepath} '{download_link}' && unzip {geolite_asn_zip_filepath} && rm -f {geolite_asn_zip_filepath} && mv GeoLite*/* . && rm -f {geolite_asn_ipv6_csv_filepath} && rm -f COPYRIGHT.txt LICENSE.txt && rm -rf GeoLite*/")
        print(colored("\nDone!\n", "red"))

        # Extracting and saving database file size locally
        try:
            response = requests.head("{}".format(download_link), headers={'User-Agent': useragent}, timeout = 10)
        except:
            print(colored("[*] Timed out while trying to connect to the database server, please run the tool again.", "red"))
            sys.exit(1)

        with open(geolite_asn_filesize_filepath, "w+") as filesize:
            filesize.write(response.headers['Content-Length'])
    # else:
    #     # Checking if there is a new database change and download a new copy if applicable
    #     try:
    #         response = requests.head("{}".format(download_link), headers={'User-Agent': useragent}, timeout = 10)
    #     except:
    #         print(colored("[*] Timed out while trying to the database server, please run the tool again.", "red"))
    #         sys.exit(1)
    #     with open(geolite_asn_filesize_filepath, "r") as filesize:
    #         for line in filesize:
    #             if line == response.headers['Content-Length']:
    #                 pass
    #             else:
    #                 print(colored("[*] It seems like you have not updated the database.","red"))
    #                 try: input = raw_input #fixes python 2.x and 3.x input keyword
    #                 except NameError: pass
    #                 choice = input(colored("[?] Do you want to update now? [Y]es [N]o, default: [N] ", "red"))
    #                 if choice.upper() == "Y":
    #                     os.system("rm -rf GeoLite2*")
    #                     print(colored("[*] Downloading a new copy of the database ...\n","red"))
    #                     os.system("wget -O GeoLite2-ASN-CSV.zip '{} && unzip GeoLite2-ASN-CSV.zip && rm -f GeoLite2-ASN-CSV.zip && mv GeoLite*/* . && rm -f GeoLite2-ASN-Blocks-IPv6.csv  && rm -f COPYRIGHT.txt LICENSE.txt && rm -rf GeoLite*/".format(download_link))

    #                     try:
    #                         response = requests.get("{}".format(download_link), headers={'User-Agent': useragent}, timeout = 10)
    #                     except:
    #                         print(colored("[*] Timed out while trying to the database server, please run the tool again.", "red"))
    #                         sys.exit(1)
    #                     print("\nDone!\n")
    #                     with open("/tmp/filesize.txt", "w") as filesize:
    #                         filesize.write(response.headers['Content-Length'])
    #                 else: pass

def extract_asn(organization):
    #read csv, and split on "," the line
    asn_ipv4 = csv.reader(open('/tmp/GeoLite2-ASN-Blocks-IPv4.csv', "r"), delimiter=",")
    #loop through csv list
    for row in asn_ipv4:
        #if current rows 2nd value is equal to input, print that row
        if organization.upper().replace('_', ' ') in row[2].upper():
            return(row[1])

def extract_ip(asn, organization, output_path):

    if not output_path:
        output_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'output')

    path_ipv6 = os.path.join(output_path, organization + "_ipv6.txt")
    path_ipv4 = os.path.join(output_path, organization + "_ipv4.txt")

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    ipinfo = "https://ipinfo.io/"

    try:
        response = requests.get(ipinfo + "AS" + asn)
    except:
        print(colored("[*] Timed out while trying to the ASN lookup server, please run the tool again.", "red"))
        sys.exit(1)

    html = response.content
    soup = BeautifulSoup(html, 'html.parser')
    ipv6 = []
    ipv4 = []
    for link in soup.find_all('a'):
        if asn in link.get('href'):
            search_criteria = '/' + "AS" + asn + '/'
            ip = re.sub(search_criteria, '', link.get('href'))
            if "robtex" not in ip:
                if ":" in ip:
                    ipv6.append(ip)
                else: ipv4.append(ip)
            else: pass

    print(colored("[*] IP addresses owned by {} are the following (IPv4 or IPv6):".format(organization),"green"))

    if ipv4:
        print(colored("\n[*] IPv4 addresses saved to: ", "green"))
        print(colored("{}\n".format(path_ipv4), "yellow"))
        with open(path_ipv4, "w") as dump:
            for i in ipv4:
                dump.write(i + "\n")
                print(colored(i, "yellow"))

    if ipv6:
        print(colored("\n[*] IPv6 addresses saved to: ", "green"))
        print(colored("{}\n".format(path_ipv6), "yellow"))
        with open(path_ipv6, "w") as dump:
            for i in ipv6:
                dump.write(i + "\n")
                print(colored(i, "yellow"))

if __name__ == '__main__':
    banner()
    org = (parse_args().org).replace(' ', '_')
    license_key = parse_args().license
    output_path = parse_args().output
    
    useragent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:64.0) Gecko/20100101 Firefox/64.0'
    download_link = 'https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-ASN-CSV&license_key={}&suffix=zip'.format(license_key)

    check_licensekey(license_key)
    
    download_db(download_link, org, useragent)

    #extract_ip(extract_asn(org), org, output_path)