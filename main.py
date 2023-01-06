# Import the necessary libraries
from bs4 import BeautifulSoup
import requests
import time
import random
import ast
import lxml
import os
import re
import datetime
from matplotlib import pyplot as plt

userid = "ur102308292" # your id here: ur294914023 for example.
link = f"https://www.imdb.com/user/{userid}/ratings?ref_=nv_usr_rt_4"
baseUrl = "https://www.imdb.com"
gettingData = True
gettingTVData = False

IMDBData = {}
compiledIMDBData = {}
progress = {}   
progress["time"]: float = 0 
session_request = requests.session()
clear = lambda: os.system("cls")
pattern = re.compile(r"Rated on")

# Make a GET request to the URL
def loadData(name):
    with open(f"{name}.txt", "r", encoding="UTF-8") as f:
        s = f.read()
    IMDBData = ast.literal_eval(s)
    return IMDBData

def saveData(dict, name):
    with open(f'{name}.txt', 'wt', encoding="UTF-8") as data:
        data.write(str(dict))   
    
def getSiteData(link):
    r = session_request.get(link)
    return BeautifulSoup(r.content, "lxml")

def getNewPage(data, baseUrl):
    for a in data.find_all("a", class_="flat-button lister-page-next next-page", href=True):
        return baseUrl + a["href"]
    
def getIMDBID(data):
    for a in data.find_all("a", href=True):
        href = a["href"]
        splitHREF = href.split("/")
        return splitHREF[2]
    
    return 
def progressBarShow(total, current, time):
    progress["max"] = total
    progress["current"] = current
    progress["time"] += time
    progress["pages-left"] = total - current
    
    clear()
    print(f"Getting TV-Show Data:\n{progress['current']/progress['max']*100:.2f}% - Estimated Time: {progress['pages-left']*(progress['time']/(progress['current'])):.1f}s - Elapsed Time: {progress['time']:.1f}s - {current}/{total} - Request: {time:.1f}s")
    
def progressBar(pageData, elapsed, page):
    data = pageData.find_all("span", class_="pagination-range")
    for values in data:
        values = values.text.split()
        maxVal = "".join(values[-1].split(","))
        minVal = "".join(values[0].split(","))
        progress["max"] = int(maxVal)
        progress["current"] = int(minVal)
        
    maxPage = int(progress['max']/100)
    progress["time"] += elapsed
    progress["pages-left"] = maxPage - page
    
    clear()
    print(f"Getting Basic Data:\n{progress['current']/progress['max']*100:.2f}% - Estimated Time: {progress['pages-left']*(progress['time']/(page+1)):.1f}s - Elapsed Time: {progress['time']:.1f}s - {page}/{maxPage} - Request: {elapsed:.1f}s")
    
def createIMDBData(pageData, page):  
    allData = pageData.find_all("div", class_="lister-item-content")
    for count, data in enumerate(allData):
        selected = data.find("span", class_="lister-item-index unbold text-primary").text
        selected = int("".join(selected.split(",")))
        IMDBData[selected] = {}
        IMDBData[selected]["title"] = data.find("a").text
        IMDBData[selected]["id"] = getIMDBID(data)
        IMDBData[selected]["release"] = data.find("span", class_="lister-item-year text-muted unbold").text
        IMDBData[selected]["date-rated"] = data.find("p", class_="text-muted", text=pattern).text
        try:  
            IMDBData[selected]["runtime"] = data.find("span", class_="runtime").text   

        except:
            IMDBData[selected]["runtime"] = "0 min"
        try: 
            IMDBData[selected]["genres"] = data.find("span", class_="genre").text
        except:
            IMDBData[selected]["genres"] = "none"
            
        #try except to check if it has a certiface since not all of them have it adds 0 to not destroy calculations.
        try:
            IMDBData[selected]["certificate"] = data.find("span", class_="certificate").text
        except:
            IMDBData[selected]["certificate"] = "0"
    
    #gets the global rating and your personal rating. Somehow got the global one but that was by mistake :)      
        multimediaRating = data.find_all("span", class_="ipl-rating-star__rating")   
        for count, data in enumerate(multimediaRating):
            if count % 24 == 0:
                IMDBData[selected]["global-rating"] = data.text
                IMDBData[selected]["my-rating"] = multimediaRating[count + 1].text
                
          
        
    # write dict to textfile for save keeping
    saveData(IMDBData, "IMDBData")
    
def getMinutesFromRuntime(runtime):
    minutes = 0
    runtime = runtime.split()
    if len(runtime) == 4:
        minutes += int(runtime[0]) * 60
        minutes += int(runtime[2])
    if len(runtime) <= 2:
        minutes += int(runtime[0])
        
    return minutes

def refactorDate():
    months = {"Jan": 1, "Feb": 2, "Mar": 0, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
    for key, value in IMDBData.items():
        date = value["date-rated"].split()
        value["date-rated"] = (int(date[-1]), months[date[3]], int(date[2]))
        
    saveData(IMDBData, "IMDBData")
    
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
    data = {}
    #converts the sorted genres back into a dictionary.
    for i in compiledIMDBData["genre-amount"]:
        name = i[0]
        amount = i[1]
        data[name] = amount
    compiledIMDBData["genre-amount"] = data    
    
def removeDuplicates():
    media = []
    newData = {}
    for key, value in IMDBData.items():
        if value["id"] not in media:
            IMDBData[key] = {}
            media.append(value["id"])
            newData[key] = value
            
        elif value["id"] in media:
            print("Duplicate detected")
            
    saveData(newData, "IMDBData")         
    
def compileAllData():
    #opening dictionaries
    compiledIMDBData["total-media"]: int = 0
    compiledIMDBData["total-movies"]: int = 0
    compiledIMDBData["total-shows"]: int = 0
    compiledIMDBData["watchtime-movies"]: int = 0
    compiledIMDBData["watchtime-shows"]: int = 0
    compiledIMDBData["watchtime"]: int = 0
    compiledIMDBData["episodes"]: int = 0
    compiledIMDBData["global-rating"]: int = 0
    compiledIMDBData["personal-rating"]: int = 0
    compiledIMDBData["genre-amount"] = {}
    compiledIMDBData["media-per-month"] = {}
               
    for key, value in IMDBData.items():
        if "episodes" not in value:
            compiledIMDBData["total-movies"] += 1
            compiledIMDBData["watchtime-movies"] += getMinutesFromRuntime(value["runtime"])
            
        if "episodes" in value:
            compiledIMDBData["watchtime-shows"] += getMinutesFromRuntime(value["runtime"])
            compiledIMDBData["total-shows"] += 1
            compiledIMDBData["episodes"] += int(value["episodes"])
            
        compiledIMDBData["total-media"] += 1 
        compiledIMDBData["watchtime"] += getMinutesFromRuntime(value["runtime"])   
        compiledIMDBData["global-rating"] += float(value["global-rating"])
        compiledIMDBData["personal-rating"] += int(value["my-rating"])
        
        genres = value["genres"]
        compileGenresIntoList(genres)
            
            
            
    sortGenres() # converts the dictionary to a list and tuples.        
    
def printDataAllFancy():
    print(f"\n\n\n\n\nIn total you have spent {compiledIMDBData['watchtime-movies']/60:.0f} hours watching {compiledIMDBData['total-movies']} movies while also managing to watch {compiledIMDBData['total-shows']} tv-shows in {compiledIMDBData['watchtime-shows']/60:.0f} hours. \nIn total you watched {compiledIMDBData['total-media']} tv-shows and movies over {compiledIMDBData['watchtime']/60:.0f} hours. How crazy! \nThat's {compiledIMDBData['watchtime']/525948*100:.2f} % of a year or {compiledIMDBData['watchtime']/365:.0f} minutes everyday.\nYou also dived into multiple genres where these where in your top 6:")
    for count, data in enumerate(compiledIMDBData["genre-amount"]):
        if count >= 6:
            break
        print(f"{compiledIMDBData['genre-amount'][data]}st - {data}")
    print(f"\nYou rated all these an average of {compiledIMDBData['personal-rating']/compiledIMDBData['total-media']:.1f}/10 while the entirety of IMDB got an average of {compiledIMDBData['global-rating']/compiledIMDBData['total-media']:.1f}/10")
            
    
def findTVMazeData(data, selected):
    name = data["title"]
    try:
        ID = data["id"]
        mazeData = requests.get(f"https://api.tvmaze.com/lookup/shows?imdb={ID}").json()
        mazeID = mazeData["id"]
    except:
        pass
        # i know error so pass, fills up teriminal
        try:
            name = data["title"]
            mazeData = requests.get(f"https://api.tvmaze.com/singlesearch/shows?q={name}").json()
            mazeID = mazeData["id"]
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
        pass
        #did not get any data
                
def updateIMDBData(data, dict):
    #clean the data
    data = [i for i in data if i is not None]
    #loop thru data and add it to IMDBData
    for info in data:
        dict[info[-1]]["runtime"] = str(info[0])
        dict[info[-1]]["episodes"] = str(info[1])
    return dict

if not gettingData:
    IMDBData = loadData("IMDBData")
    
page: int = 0
while gettingData:
    start = time.time()
    antiBot = random.uniform(0.2, 0.5)
    time.sleep(antiBot)
    soup = getSiteData(link)
    link = getNewPage(soup, baseUrl)
    createIMDBData(soup, page)
    elapsed = time.time() - start
    progressBar(soup, elapsed, page)
    
# Loop through the results and save the text of each element
             
    page += 1   
    if link is None:
        print("Got all multimedia data!")
        removeDuplicates()
        gettingData = False
        gettingTVData = True
            
                   
while gettingTVData:
    IMDBData = loadData("IMDBData")
    # scuffed way to get a progress bar for tv-shows   
    progress = {}
    progress["time"] = 0
    total = 0
    current = 0
    for key, value in IMDBData.items():
        if "–" in value["release"]:
            total += 1
            
    newData = []
    for key, value in IMDBData.items():
        if "–" in value["release"]:
            start = time.time()
            current += 1
            newData.append(findTVMazeData(value, key))
            progressBarShow(total, current, time.time()-start)
            
    saveData(updateIMDBData(newData, IMDBData), "IMDBData")
    gettingTVData = False
    
if not gettingData:
    IMDBData = loadData("IMDBData")
    refactorDate()
    compileAllData()  
    printDataAllFancy()
    saveData(compiledIMDBData, "CompiledData")