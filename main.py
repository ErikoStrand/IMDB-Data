# Import the necessary libraries
from bs4 import BeautifulSoup
import requests
import time
import random
import json

link = f"https://www.imdb.com/user/ur102308292/ratings?ref_=nv_usr_rt_4"
baseUrl = "https://www.imdb.com"
gettingData = False
IMDBData = {}

# Make a GET request to the URL
def getSiteData(link):
    r = requests.get(link)
    return BeautifulSoup(r.content, features="html.parser")

def getNewPage(data, baseUrl):
    for a in data.find_all("a", class_="flat-button lister-page-next next-page", href=True):
        return baseUrl + a["href"]
    
def createIMDBData(INData, page):    
    multimediaTitle = INData.find_all("h3", class_="lister-item-header")
    for count, data in enumerate(multimediaTitle):
        selected = int(data.find("span", class_="lister-item-index unbold text-primary").text)
        IMDBData[selected] = {}
        IMDBData[selected]["title"] = data.find("a").text
        IMDBData[selected]["release"] = data.find("span", class_="lister-item-year text-muted unbold").text
    
    multimediaInformation = INData.find_all("p", class_="text-muted text-small")
    for count, data in enumerate(multimediaInformation):   
        if count % 3 == 0:
            selected = int((count + 3) / 3 + (page * 100))            
            try:    
                IMDBData[selected]["runtime"] = data.find("span", class_="runtime").text
            except:
                IMDBData[selected]["runtime"] = "0min"
            try: 
                IMDBData[selected]["genres"] = data.find("span", class_="genre").text
            except:
                IMDBData[selected]["genre"] = "none"
                
            #try except to check if it has a certiface since not all of them have it adds 0 to not destroy calculations.
            try:
                IMDBData[selected]["certificate"] = data.find("span", class_="certificate").text
            except:
                IMDBData[selected]["certificate"] = "0"
            
    # write dict to textfile for save keeping
    with open('dict.txt', 'wt', encoding="UTF-8") as data:
        data.write(str(IMDBData))
        
def getMovieWatchtime():
    with open("dict.txt") as f:
        data = f.read()
        IMDBData = json.loads(data)
    
    print(IMDBData)
        
    watchtime: int = 0
    for key, value in IMDBData.items():
            pass
        
getMovieWatchtime()   
page: int = 0
while gettingData:
    antiBot = random.randint(1, 3)
    print(f"Waiting {antiBot} s")
    time.sleep(antiBot)
    
    soup = getSiteData(link)
    link = getNewPage(soup, baseUrl)
    createIMDBData(soup, page)
    
# Loop through the results and save the text of each element
            
    print(f"Completed page nmr {page}") 
    page += 1   
    if link is None:
        gettingData = False
    
#<span class="ipl-rating-star__rating">7</span> rating
#