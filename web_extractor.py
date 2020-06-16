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
        parts = re.split("\/", url)
        match = re.match("([\w\-]+\.)*([\w\-]+\.\w{2,6}$)", parts[2]) 
        if match != None:
            if re.search("\.uk", parts[2]): 
                match = re.match("([\w\-]+\.)*([\w\-]+\.[\w\-]+\.\w{2,6}$)", parts[2])
            return match.group(2).split(".")[0]
        else: return ''


def mediafire(url):
    try:
        response = requests.get(url, allow_redirects=False)
        if(response.status_code == 404):
            print("Invalid Mediafire URL \n")
        else:
            soup = BeautifulSoup(response.text, features='lxml')
            x = soup.findAll("a", {"class": "input popsok"})
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
        response = requests.get(
            url, headers={'Cookie': '', 'User-Agent': 'Mozilla/5.0'})
        if(response.status_code == 404):
            print("Invalid Google Drive URL \n")
        else:
            soup = BeautifulSoup(response.text,'lxml')
            return (soup.findAll("meta", {"itemprop": "name"})[0]['content'],FILE_URL.format(id=id, confirm=''))
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)


def dropbox(url):
    try:
        response = requests.get(url.replace("?dl=0", "?dl=1"), headers={
                                'Cookie': '', 'User-Agent': 'Mozilla/5.0'})
        if(response.status_code == 404):
            print("Invalid Dropbox URL \n")
        else:
            return response.url
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)


def github(url):
    try:
        response = requests.head(
            url, headers={'Cookie': '', 'User-Agent': 'Mozilla/5.0'})
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
            soup = BeautifulSoup(session.get(
                response.url).text, features='lxml')
            x = soup.findAll("a", {"class": "btn btn-lg btn-danger"})
            if (x != []):
                for a in x:
                    return (a['download'],a['href'])
            else:
                print("Invalid Youtube URL \n")
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)


def facebook(url):
    try:
        with requests.Session() as session:
            response = session.post("https://keepvid.works/?url="+url+"#dlURL")
            soup = BeautifulSoup(session.get(
                response.url).text, features='lxml')
            x = soup.findAll("a", {"class": "btn btn-lg btn-danger"})
            if (x != []):
                for a in x:
                    return a['href']
            else:
                print("Invalid Youtube URL \n")
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

def get_file_name(url):
    web_domain = getDomain(url)
    if(web_domain == 'googleusercontent'):
        response = requests.get(url.split("?e=download")[0].split("/")[-1])
        if(response.status_code == 404):
            print("Invalid URL \n")
        else:
            soup = BeautifulSoup(response.text,'lxml')
            return soup.findAll("meta", {"itemprop": "name"})[0]['content']
    elif(web_domain == "googlevideo"):
        return "videoplayback.mp4"
    elif(web_domain == 'dropboxusercontent'):
        response = requests.head(url)
        if(response.status_code == 404):
            print("Invalid URL \n")
        else:
            return response.headers['Content-Disposition'].split("'")[-1]
    else:
        return re.search(r'(?<=\/)[^\/\?#]+(?=[^\/]*$)', url).group(0)

def redirect_url(url):
    web_domain = getDomain(url)
    if(web_domain == 'github'):
            return requests.head(url)
    else:
        with requests.Session() as session:
            return session.head(session.post(url).url)


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
        link_type = requests.head(link).headers
    if('Content-Type' in link_type):  # True if this url is text/html, False if is a file
        web_domain = getDomain(link)
        if web_domain in domain_crawler_mapper:
            return domain_crawler_mapper[web_domain](link)
        else:
            return "Not supported this domain."
    else:
        return link


if __name__ == "__main__":
    data = guess_type_of(
        'https://www.facebook.com/rgb.vn/videos/1396783103844096/')
    print(data)
