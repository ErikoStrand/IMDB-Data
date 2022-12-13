# Import the necessary libraries
from bs4 import BeautifulSoup
import requests
import time
import random
import ast
import matplotlib.pyplot as plt
import re

link = f"https://www.imdb.com/user/ur102308292/ratings?ref_=nv_usr_rt_4"
baseUrl = "https://www.imdb.com"
gettingData = False

IMDBData = {}
compiledIMDBData = {}

# Make a GET request to the URL
def getSiteData(link):
    r = requests.get(link)
    return BeautifulSoup(r.content, features="html.parser")

def getNewPage(data, baseUrl):
    for a in data.find_all("a", class_="flat-button lister-page-next next-page", href=True):
        return baseUrl + a["href"]
    
    
def createIMDBData(pageData, page):    
    multimediaTitle = pageData.find_all("h3", class_="lister-item-header")
    for count, data in enumerate(multimediaTitle):
        selected = int(data.find("span", class_="lister-item-index unbold text-primary").text)
        IMDBData[selected] = {}
        IMDBData[selected]["title"] = data.find("a").text
        IMDBData[selected]["release"] = data.find("span", class_="lister-item-year text-muted unbold").text
                
    multimediaInformation = pageData.find_all("p", class_="text-muted text-small")
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
    
    #gets the global rating and your personal rating. Somehow got the global one but that was by mistake :)      
    multimediaRating = pageData.find_all("span", class_="ipl-rating-star__rating")   
    selected = 0 + (page * 100)
    for count, data in enumerate(multimediaRating):
        if count % 24 == 0:
            selected += 1
            IMDBData[selected]["global-rating"] = data.text
            IMDBData[selected]["my-rating"] = multimediaRating[count + 1].text
            
    #get the date you rated the media:
    pattern = re.compile(r"Rated on") # using this you can a tag that contains a specific text.
    multimediaRatedOn = pageData.find_all("p", class_="text-muted", text = pattern) 
    for count, data in enumerate(multimediaRatedOn):
        selected = count + 1
        IMDBData[selected]["rated-on"] = data.text.replace("Rated on", "")
        
    # write dict to textfile for save keeping
    with open('dict.txt', 'wt', encoding="UTF-8") as data:
        data.write(str(IMDBData))
        
def getMinutesFromRuntime(runtime):
    minutes = 0
    runtime = runtime.split()
    if len(runtime) == 4:
        minutes += int(runtime[0]) * 60
        minutes += int(runtime[2])
    if len(runtime) == 2:
        minutes += int(runtime[0])
        
    return minutes

def compileGenresIntoList(genres):
    genres = genres.replace(",", "").lower()
    genres = genres.split()
    for genre in genres:
        try:
            compiledIMDBData["genre-amount"][genre] += 1
        except:
            compiledIMDBData["genre-amount"][genre] = 0
            
def sortGenres():
    compiledIMDBData["genre-amount"] = sorted(compiledIMDBData["genre-amount"].items(), key=lambda x: x[1], reverse=True)
    
def compileMovieData():
    #opening dictionaries
    compiledIMDBData["total-movies"]: int = 0
    compiledIMDBData["watchtime"]: int = 0
    compiledIMDBData["global-rating"]: int = 0
    compiledIMDBData["personal-rating"]: int = 0
    compiledIMDBData["genre-amount"] = {}
    
    with open("dict.txt", "r", encoding="UTF-8") as f:
        s = f.read()
        IMDBData = ast.literal_eval(s)
               
    for key, value in IMDBData.items():
        #removes shows from calculations
        if "–" not in value["release"]:
            compiledIMDBData["total-movies"] += 1
            compiledIMDBData["watchtime"] += getMinutesFromRuntime(value["runtime"])
            compiledIMDBData["global-rating"] += float(value["global-rating"])
            compiledIMDBData["personal-rating"] += int(value["my-rating"])
            compileGenresIntoList(value["genres"])
            
            
            
    sortGenres() # converts the dictionary to a list and tuples.        
    print(compiledIMDBData)
    
def createShowData(pageData, selected):
    episodeCount = int(pageData.find("span", class_="sc-89e7233a-3 kNoqWq").text)
    print(episodeCount)
    
page: int = 0
while gettingData:
    antiBot = random.randint(0, 2)
    print(f"Waiting {antiBot} s")
    time.sleep(antiBot)
    
    soup = getSiteData(link)
    link = getNewPage(soup, baseUrl)
    createIMDBData(soup, page)
    
# Loop through the results and save the text of each element
            
    print(f"Completed page nmr {page}") 
    page += 1   
    if link is None:
        print("Got all multimedia data!")
        gettingData = False
        

if not gettingData:
    compileMovieData()  