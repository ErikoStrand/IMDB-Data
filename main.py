# Import the necessary libraries
from bs4 import BeautifulSoup
import requests
import time
import random
import ast
import matplotlib.pyplot as plt
import re

userid = "" # your id here: ur294914023 for example.
link = f"https://www.imdb.com/user/{userid}/ratings?ref_=nv_usr_rt_4"

baseUrl = "https://www.imdb.com"
gettingData = True
gettingTVData = False

IMDBData = {}
compiledIMDBData = {}
    
# Make a GET request to the URL
def loadData():
    with open("IMDBData.txt", "r", encoding="UTF-8") as f:
        s = f.read()
    IMDBData = ast.literal_eval(s)
    return IMDBData

def saveData(dict):
    with open('IMDBData.txt', 'wt', encoding="UTF-8") as data:
        data.write(str(dict))   
    
def getSiteData(link):
    r = requests.get(link)
    return BeautifulSoup(r.content, features="html.parser")

def getNewPage(data, baseUrl):
    for a in data.find_all("a", class_="flat-button lister-page-next next-page", href=True):
        return baseUrl + a["href"]
    
def getIMDBID(data):
    for a in data.find_all("a", href=True):
        href = a["href"]
        splitHREF = href.split("/")
        return splitHREF[2]
    
    return 
def createIMDBData(pageData, page):    
    multimediaTitle = pageData.find_all("h3", class_="lister-item-header")
    for count, data in enumerate(multimediaTitle):
        selected = int(data.find("span", class_="lister-item-index unbold text-primary").text)
        IMDBData[selected] = {}
        IMDBData[selected]["title"] = data.find("a").text
        IMDBData[selected]["id"] = getIMDBID(data)
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
    saveData(IMDBData)
      
def getMinutesFromRuntime(runtime):
    minutes = 0
    runtime = runtime.split()
    if len(runtime) == 4:
        minutes += int(runtime[0]) * 60
        minutes += int(runtime[2])
    if len(runtime) <= 2:
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
    
def removeDuplicates():
    media = []
    newData = {}
    for key, value in IMDBData.items():
        if value["id"] not in media:
            IMDBData[key] = {}
            media.append(value["id"])
            newData[key] = value
            
        elif value["id"] in media:
            print("Duplicate detexted")
            
    saveData(newData)
            
def compileAllData():
    #opening dictionaries
    compiledIMDBData["total-movies"]: int = 0
    compiledIMDBData["watchtime"]: int = 0
    compiledIMDBData["episodes"]: int = 0
    compiledIMDBData["global-rating"]: int = 0
    compiledIMDBData["personal-rating"]: int = 0
    compiledIMDBData["genre-amount"] = {}
               
    for key, value in IMDBData.items():
        compiledIMDBData["total-movies"] += 1
        compiledIMDBData["watchtime"] += getMinutesFromRuntime(value["runtime"])
        compiledIMDBData["global-rating"] += float(value["global-rating"])
        compiledIMDBData["personal-rating"] += int(value["my-rating"])
        try:
            compiledIMDBData["episodes"] += int(value["episodes"])
        except:
            # i know erorr, its a movie not a show. so episodes dont exsist.
            pass
        
        compileGenresIntoList(value["genres"])
            
            
            
    sortGenres() # converts the dictionary to a list and tuples.        
    print(compiledIMDBData)
    
    
def findTVMazeData(data, selected):
    if "–" in data["release"]:
        time.sleep(0.2)
        name = data["title"]
        try:
            ID = data["id"]
            mazeData = requests.get(f"https://api.tvmaze.com/lookup/shows?imdb={ID}").json()
            mazeID = mazeData["id"]
            print(f"got data for, {name}, with ID")   
        except:
            pass
            # i know error so pass, fills up teriminal
            try:
                name = data["title"]
                mazeData = requests.get(f"https://api.tvmaze.com/singlesearch/shows?q={name}").json()
                mazeID = mazeData["id"]
                print(f"got data for, {name}, with name")
            except:
                pass
                #i know error so pass, fills up terminal

            
        try:
            showData = requests.get(f"https://api.tvmaze.com/shows/{mazeID}/episodes").json()
            minutes = 0
            episodes = 0
            for value in showData:
                try:
                    minutes += value["runtime"]
                    lastmin = value["runtime"]
                except:
                    minutes += lastmin

                episodes += 1

            return (minutes, episodes, selected)
        
        except:
            print(f"could not get any data using tvmaze :(, {name}")

def updateIMDBData(data, dict):
    #clean the data
    data = [i for i in data if i is not None]
    #loop thru data and add it to IMDBData
    for info in data:
        dict[info[-1]]["runtime"] = str(info[0])
        dict[info[-1]]["episodes"] = str(info[1])
    return dict

if not gettingData:
    IMDBData = loadData()
    
page: int = 0
while gettingData:
    antiBot = random.uniform(0.2, 1.3)
    print(f"Waiting {antiBot} s")
    time.sleep(antiBot)
    
    soup = getSiteData(link)
    link = getNewPage(soup, baseUrl)
    createIMDBData(soup, page)
    
# Loop through the results and save the text of each element
            
    print(f"got data for page {page}") 
    page += 1   
    if link is None:
        print("Got all multimedia data!")
        removeDuplicates()
        gettingData = False
        gettingTVData = True
        
while gettingTVData:
    IMDBData = loadData()
    newData = []
    for key, value in IMDBData.items():
        newData.append(findTVMazeData(value, key))
    
    saveData(updateIMDBData(newData, IMDBData))
    gettingTVData = False
    
if not gettingData:
    IMDBData = loadData()
    #compile a list of all the shows that are watched.
    
    compileAllData()  