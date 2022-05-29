#!/usr/bin/env python
# coding: utf-8

# In[23]:


import requests
from requests.auth import HTTPBasicAuth
import datetime
import re
import base64
import json


# In[36]:


def readOnlyLine(fileName):
    with open(f'{fileName}') as f:
        return next(f)
    
def music_handler(f, o):
    current_line = next(f)
    if current_line[0] == "!":
        o.write("!--------MUSIC END-------------\n\n")
        return current_line 
    
    trackLink = current_line.strip()
    parameters = {"url": trackLink, "format": "json"}
    website = re.search('\/\/(.+?)\/', trackLink).group(1)
    trackJson = requests.get(f'https://{website}/oembed', params = parameters).json()
    trackThumb = trackJson['thumbnail_url']
    trackTitle = trackJson['title']
    htmlBlock = f'<div class="ach skew-x-6"> <a href="{trackLink}"><img class="ach-img" src={trackThumb}/></a><p class="musicgi-title">{trackTitle}</p></div>\n\n'
    o.write(htmlBlock)
    music_handler(f, o)
    
def playlist_handler(o):
    o.write("!--------PLAYLISTS-------------\n")
    parameters = {"grant_type": "client_credentials", "client_id": readOnlyLine("spotifyID.txt"), "client_secret": readOnlyLine("spotifySecret.txt")}
    
    authJson = requests.post(f'https://accounts.spotify.com/api/token', 
                             params = parameters,
                             headers={
                                 'Content-Type': "application/x-www-form-urlencoded"
                             }).json()

    accessToken = authJson['access_token']
    playlistsJson = requests.get(f'https://api.spotify.com/v1/users/22kb7mgop3ckzk6wvv7h6qnqy/playlists',
                                 params = parameters,
                                 headers={
                                     'Authorization': f'Bearer {accessToken}',
                                     'Content-Type': "application/json"
                                 }).json()
    
    for items in playlistsJson['items']:
        playlistLink = f'https://open.spotify.com/playlist/{items["id"]}'
        try:
            imgSrc = items['images'][0]['url']
        except:
            continue
        playlistTitle = items['name']
        htmlBlock = f'<div class="ach skew-x-6"> <a href="{playlistLink}"><img class="ach-img" src={imgSrc}/></a><p class="playlist-title">{playlistTitle}</p></div>\n\n'
        o.write(htmlBlock)
    o.write("!--------PLAYLISTS END----------\n\n")
    return
    
def git_handler(o):
    o.write("!--------PROJECTS START----------\n\n")
    parameters = {"username": "QuinnDACollins", "type":"owner", "sort":"pushed", "per_page":"5"}
    repoJson = requests.get(f'https://api.github.com/user/repos', 
                             auth = HTTPBasicAuth('QuinnDACollins', readOnlyLine("gitSecret.txt")),
                             params=parameters
                             ).json()
    for repo in repoJson:
        repoTitle = repo['full_name']
        repoThumbJson = requests.get(f'https://api.github.com/repos/{repoTitle}/contents/thumb.png', 
                             auth = HTTPBasicAuth('QuinnDACollins', readOnlyLine("gitSecret.txt")),
                             params=parameters
                             ).json()
        try:
            imgSrc = repoThumbJson['download_url']
        except:
            imgSrc = "data/gitpl.png"
        repoLink = repo['svn_url']
        repoName = repo['name']
        htmlBlock = f'<div class="ach skew-x-6"> <a href="{repoLink}"><img class="ach-img" src={imgSrc}/></a><p class="playlist-title">{repoName}</p></div>\n\n'
        o.write(htmlBlock)
    o.write("!--------PROJECTS END----------\n\n")
    return

def push_to_git(outputFileName):
    print("!--------PUSHING START----------!")
    data = ""
    with open(outputFileName, 'r') as file:
        data = file.read()
    
    getFileJson = requests.get(f'https://api.github.com/repos/QuinnDACollins/QuinnDACollins.github.io/contents/data/htmlData.txt', 
                         auth = HTTPBasicAuth('QuinnDACollins', readOnlyLine("gitSecret.txt")),
                         ).json()
    fileSha = getFileJson['sha']
    encoded_data = base64.b64encode(data.encode())
    encoded_data_string = encoded_data.decode()
    message = "Update htmlData using quinnparser3000 - https://github.com/QuinnDACollins/quinnparser3000"
    parameters = {"message":"Update htmlData", 
                  "commiter": {"name": 'Quinn', "email": 'QuinnDaCollins@gmail.com'}, "content": f'{data}', "sha": "a2133a43c507cd7b1fbde2b9f95b23c5a94006e1"}
    body = {"message": f'{message}', 
            "commiter": {"name": 'Quinn Collins', "email": 'QuinnDaCollins@gmail.com'}, 
            "content": f'{encoded_data_string}', 
            "sha": f'{fileSha}'}
    bodyJson = json.dumps(body)
    
    updateFileJson = requests.put(f'https://api.github.com/repos/QuinnDACollins/QuinnDACollins.github.io/contents/data/htmlData.txt', 
                         auth = HTTPBasicAuth('QuinnDACollins', readOnlyLine("gitSecret.txt")),
                         data = bodyJson
                                 ).json()
    print("!--------PUSHING FINISH----------!")
    
with open("data.txt", "r+") as f:
    outputStr = f'output {str(datetime.datetime.now())}.txt'
    output = open(f'{outputStr}', "x")
    playlist_handler(output)
    git_handler(output)
    line = next(f)
    #check for a playlist link under the playlist flag
    # check for repeated music links under music flags and projects under project flag.
    while line != "":
        if line == "!music\n":
            output.write("!--------MUSIC-------------\n")
            line = music_handler(f, output)
            continue # so that we can check for EOF after recursion
        # elif l == "!projects":
        line = ""
    output.close()
    push_to_git(outputStr)


# In[ ]:





# In[ ]:




