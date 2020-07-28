#!/usr/bin/env python3

import tkinter
import bs4
import requests
import re
import urllib.request
import os
from PIL import Image

#loads the given URL:
def scrapePage():
    tempURL = inputTxt.get()
    res = requests.get(tempURL)
    res.raise_for_status()
    mySoup = bs4.BeautifulSoup(res.text, 'html.parser')
    modifyHTML(mySoup)

def modifyHTML(tempSoup):
    #get only the <article> content
    articleTag = tempSoup.article
    #removes the first Header
    tempTopic = articleTag.select_one("h1").getText()
    articleTag.select_one("h1").decompose()
    #removes the address -> author
    articleTag.select_one("address").decompose()
    
    #replace img src and store image url in array
    imageURLs = []
    for img in articleTag.findAll('img'):
        #add style to <img... (optional)
        #img['style'] = 'width: 100%; max-width:690px; height: auto;'
        #add image name to array
        imageURLs.append(img['src'].replace("/file/",""))
        #set new image src with lowres image
        img['src'] = img['src'].replace("/file/","/user/images/low")
        #add specific lightbox wrapper around img tag - to the normalres image
        img.wrap(tempSoup.new_tag("a",attrs={"rel": "lightbox", "href": img['src'].replace("/user/images/low","/user/images/")}))
    
    #embed youtube
    for iframe in articleTag.findAll('iframe'):
        iframe['src'] = re.sub(".+?(?<=%3D)","https://www.youtube.com/embed/",iframe['src'])
        #add div wrappers for iframe -> video
        iframe.wrap(tempSoup.new_tag("div",attrs={"class": "video-container-wrapper iloader"}))
        iframe.wrap(tempSoup.new_tag("div",attrs={"class": "video-container"}))

    #add link to telegra.ph article at bottom
    telegraphLink = tempSoup.new_tag("a",attrs={"href": inputTxt.get(), "target":"_blank"})
    telegraphLink.string = "Link to telegra.ph page: " + tempTopic
    tempSoup.article.append(telegraphLink)
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
    textArea.delete(1.0,"end")
    
    #create image folder to store the downloaded images
    if not os.path.exists('images'):
        os.makedirs('images')
    
    #download every image
    for imageURL in imageURLs:
        textArea.insert(tkinter.END, "- ")
        urllib.request.urlretrieve("https://telegra.ph/file/" + imageURL, "images/" + imageURL)
        #resize image and add "low" to image original name
        tempImage = Image.open("images/" + imageURL)
        tempImage.thumbnail((int(inputTxtThumb.get()), int(inputTxtThumb.get())))
        tempImage.save("images/low" + imageURL)
    
    textArea.insert(tkinter.END, "\nFINISHED")

#tkinter - GUI:
window = tkinter.Tk(className="telegraph scraper")
window.geometry("500x350")

greeting = tkinter.Label(window, text="URL of telegra.ph site you wish to scrape:")
greeting.grid(column=0, columnspan=5, row=1, pady = 10, padx = 10)

enterURL = tkinter.Label(window, text="URL:")
enterURL.grid(column=0, row=2, pady = 10, padx = 10)

inputTxt = tkinter.Entry(window, width=45)
inputTxt.insert(0, "")
inputTxt.grid(column=1, row=2, pady = 10, padx = 10)

enterFileName = tkinter.Label(window, text="Filename:")
enterFileName.grid(column=0, row=3, pady = 10, padx = 10)

inputTxtFile = tkinter.Entry(window, width=45)
inputTxtFile.insert(0, "test.html")
inputTxtFile.grid(column=1, row=3, pady = 10, padx = 10)

thumbnailSize = tkinter.Label(window, text="Thumb-Size:")
thumbnailSize.grid(column=0, row=4, pady = 10, padx = 10)

inputTxtThumb = tkinter.Entry(window, width=45)
inputTxtThumb.insert(0, "400")
inputTxtThumb.grid(column=1, row=4, pady = 10, padx = 10)

scrapePageBtn = tkinter.Button(window, text ="scrape page", command = scrapePage)
scrapePageBtn.grid(column=0, columnspan=2, row=5, pady = 10, padx = 10)

textArea = tkinter.Text(window, height=3, width=40)
textArea.insert(tkinter.INSERT, "- insert URL of telegra.ph site\n- choose local HTML filename\n- change Thumbnail resolution")
textArea.grid(columnspan=3, row=6, pady = 10, padx = 10)
 
window.mainloop()