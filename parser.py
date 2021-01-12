import re
from bs4 import BeautifulSoup
import requests
import csv
import sys
import argparse
import logging

logging.basicConfig(filename="logs.log", level=logging.INFO)
url = 'https://www.imdb.com/'
start = "&start="

class FilmInfo:
    name = ""
    genres = []
    rating = 0
    stars = []
    details = {}

def findFilmLinksFromPage(url):
    try:
        page = requests.get(url)
        films = []
        filmsLinks = []
        soup = BeautifulSoup(page.text, "html.parser")
        films = soup.findAll('h3',class_='lister-item-header')
        for film in films:
            link = film.find('a').get('href')
            filmsLinks.append(link)
        return filmsLinks
    except Exception as ex:
        logging.critical(ex, exc_info=True)     

def findAllFilmsLinks(url):
    result = []
    for i in range(int(250 / 250)):
        pageNumber = + i*250 + 1
        fullUrl = url + str(pageNumber)+'&count=250'
        result += findFilmLinksFromPage(fullUrl)
    return result


def getDetails(soup):
    detailDiv = soup.findAll("div", id = "titleDetails")
    for i in detailDiv[0].select("span"):
        i.extract()
    res = [list(i.stripped_strings) for i in detailDiv[0].findAll(["div"])]
    details = {}
    for i in res:
        if len(i)>1 and ":" in i[0]:
            details[i[0][:-1]] = [el for el in i[1:] if len(el)>1]
    return details


def getFilmInfo(url):
    try:
        result = FilmInfo()
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        filmName = soup.find('h1').contents[0]

        logging.info('Парсинг:' + filmName)

        ke = soup.find(id='titleStoryLine').findAll(class_='see-more inline canwrap')
        filmGenresBlocks = ke[len(ke)-1].findAll('a')
        filmGenres = []
        for genre in filmGenresBlocks:
            filmGenres.append(genre.string.strip())
        ratingBlock = soup.find('span', itemprop = 'ratingValue') 
        if ratingBlock == None:
            rating = None
        else: 
            rating = ratingBlock.string.strip()

        creditSummaryItem = soup.findAll('div', class_='credit_summary_item')
        starsBlock = creditSummaryItem[len(creditSummaryItem) -1].findAll('a')
        stars = []
        for starBlock in starsBlock:
            stars.append(starBlock.string)

        result.name = filmName.strip()
        result.genres = filmGenres
        result.stars = stars
        result.rating = rating
        result.details = getDetails(soup)
        return result
    except Exception as ex:
        logging.critical(ex, exc_info=True)    

def main(filter):
    links = findAllFilmsLinks(url+filter+start)
    result = []
    i = 0
    for link in links:
        result.append(getFilmInfo(url+link)) 

    filename = "films.csv"   
    with open(filename, "w", newline="", encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(map(lambda x: [x.name, x.genres, x.stars, x.rating, x.details], result))
    

def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', default="", required=False, help ="feature,tv_movie,tv_series,tv_special,tv_miniseries,short,video")
    parser.add_argument('--release_date', default="", required=False, help="yyyy-mm-dd,yyyy-mm-dd")
    parser.add_argument('--rating', default="", required=False, help="1.4,9.3")
    parser.add_argument('--genres', default="action", required=False, help="action,comedy,mystery")
    parser.add_argument('--countries', default="", required=False, help="af,ax,al,dz,as,ad,ao,ai")
    return parser

if __name__ == "__main__":
        parser = createParser()
        parsedArgv= parser.parse_args()
        searchString = "search/title/?title_type="+parsedArgv.type+"&release_date="\
        +parsedArgv.release_date+"&user_rating="+parsedArgv.rating+"&genres="\
        +parsedArgv.genres+"&countries="+parsedArgv.countries
        main(searchString)
    


     
