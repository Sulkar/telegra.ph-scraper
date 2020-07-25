#!/usr/bin/python

import tkinter
import bs4
import requests
import re
import urllib.request
import os

#loads the given URL:
def scrapePage():
    tempURL = inputTxt.get()
    res = requests.get(tempURL)
    res.raise_for_status()
    mySoup = bs4.BeautifulSoup(res.text, 'html.parser')
    modifyHTML(mySoup)

def modifyHTML(tempSoup):
    if(tempSoup.iframe):
        #add first div wrapper for iframe -> video
        newTagIframe1 = tempSoup.new_tag("div",attrs={"class": "video-container-wrapper iloader"})
        tempSoup.iframe.wrap(newTagIframe1)
        #add second div wrapper for iframe -> video
        newTagIframe2 = tempSoup.new_tag("div",attrs={"class": "video-container"})
        tempSoup.iframe.wrap(newTagIframe2)
    #get only the <article> content
    articleTag = tempSoup.article
    #removes the first Header
    articleTag.select_one("h1").decompose()
    #removes the address -> author
    articleTag.select_one("address").decompose()
    #replace img src and store image url in array
    imageURLs = []
    for img in articleTag.findAll('img'):
        imageURLs.append(img['src'].replace("/file/",""))
        img['src'] = img['src'].replace("/file/","/user/images/")
    #embed youtube
    for iframe in articleTag.findAll('iframe'):
        iframe['src'] = re.sub(".+?(?<=%3D)","https://www.youtube.com/embed/",iframe['src'])
    #prettify code
    saveHTMLToFile(articleTag.prettify())
    downloadAllImages(imageURLs)

#saves the data to a .html file
def saveHTMLToFile(HtmlData):
    tempFileName = inputTxtFile.get()
    file = open(tempFileName,"w+")
    tempOutput = HtmlData
    file.write(tempOutput)
    file.close()

#download all images from the given URL
def downloadAllImages(imageURLs):
    textArea.insert(tkinter.INSERT, "")
    #create image folder to store the downloaded images
    if not os.path.exists('images'):
        os.makedirs('images')
    #download every image
    for imageURL in imageURLs:
        textArea.insert(tkinter.END, "- ")
        urllib.request.urlretrieve("https://telegra.ph/file/" + imageURL, "images/" + imageURL)
    textArea.insert(tkinter.END, "\nFINISHED")

#tkinter - GUI:
window = tkinter.Tk(className="telegraph scraper")
window.geometry("500x350")

greeting = tkinter.Label(window, text="URL of telegra.ph site you wish to scrap:")
greeting.grid(column=0, columnspan=5, row=1, pady = 10, padx = 10)

enterURL = tkinter.Label(window, text="URL:")
enterURL.grid(column=0, row=2, pady = 10, padx = 10)

inputTxt = tkinter.Entry(window, width=45)
inputTxt.insert(0, "")
inputTxt.grid(column=1, row=2, pady = 10, padx = 10)

enterFileName = tkinter.Label(window, text="Filename:")
enterFileName.grid(column=0, row=3, pady = 10, padx = 10)

inputTxtFile = tkinter.Entry(window, width=45)
inputTxtFile.insert(0, ".html")
inputTxtFile.grid(column=1, row=3, pady = 10, padx = 10)

scrapePageBtn = tkinter.Button(window, text ="scrape page", command = scrapePage)
scrapePageBtn.grid(column=0, columnspan=2, row=4, pady = 10, padx = 10)

textArea = tkinter.Text(window, height=3, width=40)
textArea.insert(tkinter.INSERT, "- insert URL of telegra.ph site\n- choose local filename")
textArea.grid(columnspan=3, row=5, pady = 10, padx = 10)
 
window.mainloop()