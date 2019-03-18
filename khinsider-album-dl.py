# Installation (only has to be setup once)
# 1. Open command prompt as administrator (windows search "CMD", right click, run as admin)
# 2. Run the command "python -m pip install -U pip"
# 3. Run the command "python -m pip install HTMLParser"
# 4. Run the command "python -m pip install requests"

# Usage (must be done for each album)
# 1. Double click this file (khinsider-album-dl.py)
# 2. Enter the album of the URL to be downloaded

import requests
from html.parser import HTMLParser
import os
import sys

saveDir = ""

def main(argv):
    global saveDir

    albumUrl = input("Album URL: ")
    response = requests.get(albumUrl)
    htmlData = response.content.decode("utf-8")

    saveDir = albumUrl.split("/")[-1]
    try:
        os.mkdir(saveDir)
        print("Created folder \"{}\"".format(saveDir))
    except FileExistsError:
        print("Saving in exsisting folder \"{}\"".format(saveDir))

    saveDir += "/"
        
    albumParser = KhinsiderAlbumParser()
    albumParser.feed(htmlData)

    audioParser = KhinsiderAudioParser()
    for songStr in albumParser.songList:
        response = requests.get("https://downloads.khinsider.com" + songStr)
        audioParser.feed(response.content.decode("utf-8"))

class KhinsiderAlbumParser(HTMLParser):
    def __init__(self):
        self.listScan = False
        self.linkScan = False
        self.colSkipCount = 0
        self.songList = []
        return super().__init__()

    def handle_starttag(self, tag, attrs):
        if tag == "table" and ("id", "songlist") in attrs:
            self.listScan = True
        elif self.listScan and tag == "td" and ("class", "clickable-row") in attrs:
            if self.colSkipCount:
                self.colSkipCount -= 1
            else:
                self.colSkipCount = 2
                self.linkScan = True
        elif self.linkScan and tag == "a":
            for attr in attrs:
                if attr[0] == "href":
                    self.songList.append(attr[1])
                    return

    def handle_endtag(self, tag):
        if tag == "table" and self.listScan:
            self.listScan = False
        elif tag == "td" and self.linkScan:
            self.linkScan = False
            

class KhinsiderAudioParser(HTMLParser):
    def __init__(self):
        self.nameScan = False
        self.audioName = ""
        return super().__init__()

    def handle_starttag(self, tag, attrs):
        if tag == "audio":
            for attr in attrs:
                if attr[0] == "src":
                    download_audio(attr[1], self.audioName)

    def handle_data(self, data):
        if data.startswith("\r\n\tSong name:"):
            self.nameScan = True
        elif self.nameScan:
            self.audioName = data
            self.nameScan = False
            

def download_audio(url, audioName):
    print("downloading {}".format(audioName))
    fileExt = "."+url.split(".")[-1]
    r = requests.get(url, allow_redirects=True)
    open(saveDir + audioName + fileExt, 'wb').write(r.content)
    
if __name__ == "__main__":
    main(sys.argv[1:])
