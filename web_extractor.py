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
        response = requests.get(url,allow_redirects=False)
        if(response.status_code == 404):
            print("Invalid Mediafire URL \n")
        else:
            soup = BeautifulSoup(response.text,features='lxml')
            x=soup.findAll("a", {"class": "input popsok"})
            for a in x:
                return a['href']
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

def google(url):
    try:
        FILE_URL = 'https://docs.google.com/uc?export=download&id={id}&confirm={confirm}'
        ID_PATTERNS = [
        re.compile('/file/d/([0-9A-Za-z_-]{10,})(?:/|$)', re.IGNORECASE),
        re.compile('id=([0-9A-Za-z_-]{10,})(?:&|$)', re.IGNORECASE),
        re.compile('([0-9A-Za-z_-]{10,})', re.IGNORECASE)
        ]
    
        for pattern in ID_PATTERNS:
            match = pattern.search(url)
            if match:
                id = match.group(1)
                break
    
        url = FILE_URL.format(id=id, confirm='')
        response = requests.get(url, headers={'Cookie': '','User-Agent': 'Mozilla/5.0'})
        if(response.status_code == 404):
            print("Invalid Google Drive URL \n")
        else:
            return response.url
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

def dropbox(url):
    try:
        response = requests.get(url.replace("?dl=0", "?dl=1"), headers={'Cookie': '','User-Agent': 'Mozilla/5.0'})
        if(response.status_code == 404):
            print("Invalid Dropbox URL \n")
        else:
            return response.url
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

def github(url):
    try:
        response = requests.get(url+"/archive/master.zip", headers={'Cookie': '','User-Agent': 'Mozilla/5.0'})
        if(response.status_code == 404):
            print("Invalid Github URL \n")
        else:
            return url+"/archive/master.zip"
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

def youtube(url):
    try:
        with requests.Session() as session:
            response = session.post("https://keepvid.works/?url="+url+"#dlURL")
            soup = BeautifulSoup(session.get(response.url).text,features='lxml')
            x=soup.findAll("a", {"class": "btn btn-lg btn-danger"})
            if (x != []):
                for a in x:
                    return a['href']
            else:
                print("Invalid Youtube URL \n")
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

def facebook(url):
    try:
        with requests.Session() as session:
            response = session.post("https://keepvid.works/?url="+url+"#dlURL")
            soup = BeautifulSoup(session.get(response.url).text,features='lxml')
            x=soup.findAll("a", {"class": "btn btn-lg btn-danger"})
            if (x != []):
                for a in x:
                    return a['href']
            else:
                print("Invalid Youtube URL \n")
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)


domain_crawler_mapper = {
    "mediafire": mediafire,
    "google": google,
    "dropbox": dropbox,
    "github": github,
    "youtube": youtube,
    "facebook": facebook
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
            
        
if __name__ == "__main__":       
    data = guess_type_of('https://www.facebook.com/rgb.vn/videos/1396783103844096/')
    print(data)
