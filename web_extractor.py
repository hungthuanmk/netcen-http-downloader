# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 14:22:25 2020

@author: trand
"""
from bs4 import BeautifulSoup
import lxml
import requests
import mimetypes
import re


def getDomain(url):
    pat = r'((https?):\/\/)?(\w+\.)*(?P<domain>\w+)\.(\w+)(\/.*)?'
    m = re.match(pat, url)
    if m:
        domain = m.group('domain')
        return domain
    else:
        return False

def mediafire(url):
    try:
        page = requests.get(url).text
        soup = BeautifulSoup(page,features='lxml')
        x=soup.findAll("a", {"class": "input popsok"})
        for a in x:
            return a['href']
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

domain_crawler_mapper = {
    "mediafire": mediafire
    }

def guess_type_of(link):
    link_type, _ = mimetypes.guess_type(link)
    if link_type is None:
        link_type = requests.get(link).headers
    if( 'Content-Type' in link_type): # True if this url is text/html, False if is a file
        web_domain = getDomain(link)
        if web_domain in domain_crawler_mapper:
            return domain_crawler_mapper[web_domain](link)
        else:
            return "Not supported this domain."
    else:
        return link
            
        
       
data = guess_type_of('http://www.mediafire.com/file/8igfr1r4c9a468s/Luyen_am.doc/file')

print(data)






