from urllib import request
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv
import os
import json
import re
import ctypes
import random
import pathlib
from configparser import ConfigParser

class WallpaperScraper:
        def __init__(self):
                load_dotenv(".env")
                
                # Configuration
                configur = ConfigParser()
                configur.read('config.ini')

                # Config Subreddit Settings
                self.subreddit = configur.get("subreddit", "subreddit")
                self.link_id = configur.get("subreddit", "link_id")

                # Configuration - Wallpaper Settings
                self.MAX_PHOTOS = int(configur.get("wallpaperSettings", "max_number_of_pictures"))
                self.width = configur.get("wallpaperSettings", "width")
                self.height = configur.get("wallpaperSettings", "height")

                # Initialize Variables
                self.filenames = []
                self.numOfFiles = 0

                # Authentication using Reddit API
                auth = requests.auth.HTTPBasicAuth(os.getenv("client-id"), os.getenv("client-secret"))
                data = {'grant_type': 'password',
                        'username': os.getenv("usr"),
                        'password': os.getenv("pass")}

                headers = {"User-Agent": configur.get("application", "application_name") + "/0.0.1"} # /0.0.1 at the end

                res = requests.post('https://www.reddit.com/api/v1/access_token',
                                auth=auth, data=data, headers=headers)
                TOKEN = res.json()["access_token"]

                headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}
                requests.get('https://oauth.reddit.com/api/v1/me', headers=headers)


                res = requests.get("https://oauth.reddit.com/user/ze-robot/comments",
                                headers=headers)
                
                self.responseJSON = res.json()
                self.removeAllFilesInDirectory()

        def parseFiles(self):
                        # print(json.dumps(res.json(), indent=4, sort_keys=True))
                        # file = open("json.txt", "w", encoding="utf-8")
                        # file.write(json.dumps(res.json(), indent=4, sort_keys=True))
                        # file.close()

                        commentFile = open("comments.txt", "w")
                        for comment in self.responseJSON["data"]["children"]:
                                # print(comment["data"]["body"])
                                commentFile.write(comment["data"]["body"])
                        commentFile.close()
                        
                        print("Initializing download...")
                        with open("urls.txt", "w", encoding="utf-8") as outputFile:
                                with open("comments.txt", "r") as file:
                                        for line in file:
                                                if line[0] == "*" and line[1] == " ":
                                                        # delimitLine = delimitLine.pop()
                                                        line = re.split(r'[()*,] ', line)
                                                        line.pop(0)
                                                        line.pop(0)
                                                        for i in range(len(line)):
                                                                line[i] = re.split(r'[()]', line[i])
                                                                dimensions = line[i][0]
                                                                url = line[i][1]
                                                                # print(dimensions, url)
                                                                outputFile.write(dimensions + ", " + url + "\n")

                                                                if dimensions == "[" + str(self.width) + "×" + str(self.height) + "]":
                                                                        if not self.reachedCapacity():
                                                                                r = requests.get(url)
                                                                                if r.status_code == 404: # If you can't load the page, ignore and continue
                                                                                        print("Reached a HTTP 404 error when reaching", url)
                                                                                        continue
                                                                                self.download(url, "wallpaper")
                                                                                self.numOfFiles += 1
                                                                        else:
                                                                                return True
                                        

        def reachedCapacity(self):
                if self.numOfFiles >= self.MAX_PHOTOS:
                        print(f'Reached capacity of {self.numOfFiles}')
                        return True
                return False

        def removeAllFilesInDirectory(self):
                try:
                        print("Removing all files in wallpaper directory...")
                        dir = str(pathlib.Path().resolve()) + r"\wallpaper"
                        for f in os.listdir(dir):
                                os.remove(os.path.join(dir, f))
                        return True
                except:
                        print("Failed to remove all files from directory")
                        return False
        
        def download(self, url, pathname):
                """
                Downloads a file given an URL and puts it in the folder `pathname`
                """
                # if path doesn't exist, make that path dir
                if not os.path.isdir(pathname):
                        os.makedirs(pathname)
                # download the body of response by chunk, not immediately
                response = requests.get(url, stream=True)
                # get the total file size
                file_size = int(response.headers.get("Content-Length", 0))
                # get the file name
                filename = os.path.join(pathname, url.split("/")[-1])
                # progress bar, changing the unit to bytes instead of iteration (default by tqdm)
                progress = tqdm(response.iter_content(1024), f"Downloading {filename}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
                with open(filename, "wb") as f:
                        for data in progress.iterable:
                                # write data read to the file
                                f.write(data)
                                # update the progress bar manually
                                progress.update(len(data))
                                self.filenames.append(filename)
        
        def setWallpaper(self):
                path = str(pathlib.Path().resolve()) + r"\wallpaper"
                dir_list = os.listdir(path)
                
                # prints all files in a list
                # print(dir_list)

                rng = random.randrange(0, len(dir_list))
                fileName = dir_list[rng]
                print("Setting " + fileName + " as the wallpaper")

                SPI_SETDESKWALLPAPER = 20
                folder = str(pathlib.Path().resolve()) + "\wallpaper"
                file = folder + "\\" + str(fileName)
                ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER , 0, file, 0)
                print("Wallpaper set!")


w = WallpaperScraper()
w.parseFiles()
w.setWallpaper()