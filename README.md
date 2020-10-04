                                ____ ____ _  _ _    ____ ____ _  _ _  _ ___
                                |__| [__  |\ | |    |  | |  | |_/  |  | |__]
                                |  | ___] | \| |___ |__| |__| | \_ |__| |

                                         Author: Yassine Aboukir
 
 <p align="center"><a target="_blank" href="https://twitter.com/yassineaboukir"><img src="https://img.shields.io/twitter/follow/yassineaboukir.svg?logo=twitter"></a></p>
 

 ## Description
>An autonomous system number (ASN) is a unique number assigned to an autonomous system (AS) by the Internet Assigned Numbers Authority (IANA).
An AS consists of blocks of IP addresses which have a distinctly defined policy for accessing external networks and are administered by a single organization

This tool will search an updated database for a specific organization's ASN then use the latter to look up all IP addresses (IPv4 and IPv6) registered and owned by the organization.

<p align="center"><img width="500" src="https://i.imgur.com/xvbfM0x.png"><br>As of Jan 3rd, 2020.</p>


A web application version of this tool which was built with Flask is live on http://asnlookup.com/

## Objective
This script should be used during reconnaissance phase to identify properties owned by the company, and run a port scan on it to identify open ports and publicly exposed services.

## Usage
- Tested on Python >= 2.7 and Python 3.5. Execute the following:
```
$ git clone https://github.com/yassineaboukir/Asnlookup && cd Asnlookup
$ pip install -r requirements.txt (or pip3 install -r requirements.txt if you're using Python3)
```

- Sign up for a free account on Maxmind: `https://www.maxmind.com/en/geolite2/signup`
- Sign in and browse to `https://www.maxmind.com/en/accounts/1` > `My License Key` > `Generate new license key` > Check `No` for `Will this key be used for GeoIP Update?`.
- Open `config.py` with a text editor, and replace `key_here` placeholder with the license key you generated.

To use, execute: 

```
$ python asnlookup.py -o <Organization>`
```

_E.g: python asnlookup -o "Capital One"_



## Limitation
For smaller organizations the ASN will usually be that of their ISP whereas the hostname might not. One example of this is 207.97.227.245, a GitHub IP address. The ASN is AS27357 (Rackspace Hosting), but the hostname is pages.github.com.