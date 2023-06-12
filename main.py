# Module: main
# Author: Henk V
# Created on: 28.11.2014
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
import sys
from urllib.parse import urlencode, parse_qsl, quote
from pathlib import Path
import urllib
import xbmcgui
import xbmcplugin
import xbmcvfs
import requests
import json
import datetime
from bs4 import BeautifulSoup

from requests.auth import HTTPBasicAuth
# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

afbeelding = []
kerk = []
opnames = []
afbeelding_live = []
kerk_live = []
opnames_live = []
history_file = xbmcvfs.translatePath("special://userdata/addon_data/plugin.video.kerkdienstgemist/history.txt")
search_history = []

path = Path(history_file)
if not path.is_file():
    open(history_file, 'w').close()

    
def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urlencode(kwargs))

def list_search_history(history):
    for item in history:
        xbmc.log(str(_handle), level=xbmc.LOGERROR);

        # Create a list item with the search query
        list_item = xbmcgui.ListItem(label=item)

        # Set the appropriate URL for the list item to perform a new search
        list_item.setInfo("video", {"title": item, "mediatype": "video"})
        list_item.setPath("plugin://plugin.video.kerkdienstgemist/?zoek=" + urllib.parse.quote(item))
        zoekopdracht=urllib.parse.quote(item)
        category="video"
        url = get_url(action='zoek', category=category, zoek=zoekopdracht)
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    list_item = xbmcgui.ListItem(label='Nieuwe zoekopdracht')

    list_item.setInfo("video", {"title": "Nieuwe zoekopdracht", "mediatype": "video"})
    zoekopdracht="nieuw"
    list_item.setPath("plugin://plugin.video.kerkdienstgemist/?zoek=" + zoekopdracht)
    category="video"
    url = get_url(action='zoek', category=category, zoek=zoekopdracht)
    is_folder = True
    xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

    list_item.setInfo("video", {"title": "Geschiedenis wissen", "mediatype": "video"})
    zoekopdracht="leeg"
    list_item.setPath("plugin://plugin.video.kerkdienstgemist/?zoek=" + zoekopdracht)
    category="video"
    url = get_url(action='zoek', category=category, zoek=zoekopdracht)
    is_folder = True
    xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.endOfDirectory(_handle)

# Check if the addon was called with a search query
if len(sys.argv) > 2 and sys.argv[2]:
    # Get the search query from the URL parameters
    search_query = urllib.parse.unquote(sys.argv[2][1:])
    # Call the function to perform the search and get the results
else:
    # Read the search history from the history file
    with open(history_file, 'r') as fileobj:
        for row in fileobj:
            search_history.append((row.rstrip('\n')))

       # with open(history_file, "r+") as f:
            #search_history = f.read().splitlines()
        #    f.seek(-1, 2)  # go at the end of the file
        #    if f.read(1) != '\n':
        #        # add missing newline if not already present
        #        f.write('\n')
        #        f.flush()
        #        f.seek(0)
        #    search_history = [line[:-1] for line in f]
            # Call the function to display the search history
        list_search_history(search_history)

def list_hoofdpagina(zoekopdracht):
    xbmcplugin.setPluginCategory(_handle, 'Kerkdienstgemist')
    xbmcplugin.setContent(_handle, 'videos')
    category = 'Live'
    list_item = xbmcgui.ListItem(label=category)
    list_item.setInfo('video', {'title': category,
                                'mediatype': 'video'})
    url = get_url(action='listing', category=category, zoek=zoekopdracht)
    is_folder = True
    xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    category = 'Opnames'
    list_item = xbmcgui.ListItem(label=category)
    list_item.setInfo('video', {'title': category,
                                'mediatype': 'video'})
    url = get_url(action='listing', category=category, zoek=zoekopdracht)
    is_folder = True
    xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.endOfDirectory(_handle)

def list_live(zoekopdracht):
    for i in enumerate(kerk_live):
        category = kerk_live[i[0]]
        recording = opnames_live[i[0]]
        thumb = afbeelding_live[i[0]]
        list_item = xbmcgui.ListItem(label=category)
        list_item.setArt({'thumb': thumb,
                          'icon': thumb,
                          'fanart': thumb})
        list_item.setInfo('video', {'title': category,
                                    'mediatype': 'video'})
        url = get_url(action='listing', category=category, zoek=zoekopdracht)
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.endOfDirectory(_handle)

def list_opnames(zoekopdracht):
    for i in enumerate(kerk):
        category = kerk[i[0]]
        thumb = afbeelding[i[0]]
        recording = opnames[i[0]]

        list_item = xbmcgui.ListItem(label=category)
        list_item.setArt({'thumb': thumb,
                          'icon': thumb,
                          'fanart': thumb})
        list_item.setInfo('video', {'title': category,
                                    'mediatype': 'video'})
        url = get_url(action='listing', category=category, zoek=zoekopdracht)
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.endOfDirectory(_handle)


def list_videos(category, kerk):
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, category)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get the list of videos in the category.
    # videos = get_videos(category)
    if category in kerk:
        nummer = kerk.index(category)
        thumb = afbeelding[nummer]
        recording = opnames[nummer]
        # Iterate through videos.
        response3 = requests.get(recording,
                auth = HTTPBasicAuth('app_v1', 'Y4KBuCTXm9GbkZfL'))
        result3 = json.loads(response3.text)
        positie = 0
        for y in result3['included']:
            if 'download_url' in y['attributes'].keys():
                if y['attributes']['content_type'] == 'video/mp4':
                    vid_id = y['id']
                    url = y['attributes']['download_url']
                    datum = y['attributes']['recorded_at']
                    for i in enumerate(result3['data']):
                        pos = i[0]
                        title2 = result3['data'][pos]['attributes']['start_at']
                        if datum == title2:
                            title = result3['data'][pos]['attributes']['title']
                            description = result3['data'][pos]['attributes']['description']
                            description2 = BeautifulSoup(description)

                    #for video in videos:
                    # Create a list item with a text label and a thumbnail image.
                    list_item = xbmcgui.ListItem(label=datum)
                    # Set additional info for the list item.
                    # 'mediatype' is needed for skin to display info for this ListItem correctly.
                    dt = datetime.datetime.fromisoformat(datum)
                    datum2 = dt.strftime('%Y-%m-%d %H:%M')
                    list_item.setInfo('video', {'title': datum2 + ' - ' + title,
                                                'mediatype': 'video',
                                                'plot' : description2.get_text()})
                    # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
                    # Here we use the same image for all items for simplicity's sake.
                    # In a real-life plugin you need to set each image accordingly.
                    list_item.setArt({'thumb': thumb, 'icon': thumb, 'fanart': thumb})
                    # Set 'IsPlayable' property to 'true'.
                    # This is mandatory for playable items!
                    list_item.setProperty('IsPlayable', 'true')
                    # Create a URL for a plugin recursive call.
                    # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/wp-content/uploads/2017/04/crab.mp4
                    #url = get_url(action='play', video=video['video'])
                    # Add the list item to a virtual Kodi folder.
                    # is_folder = False means that this item won't open any sub-list.
                    is_folder = False
                    # Add our item to the Kodi virtual folder listing.
                    xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
            positie += 1
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)

def list_videos_live(category, kerk_live):
    xbmcplugin.setPluginCategory(_handle, category)
    xbmcplugin.setContent(_handle, 'videos')
    if category in kerk_live:
        nummer = kerk_live.index(category)
        thumb = afbeelding_live[nummer]
        recording_live = opnames_live[nummer]
        response3_live = requests.get(recording_live,
                auth = HTTPBasicAuth('app_v1', 'Y4KBuCTXm9GbkZfL'))
        result3_live = json.loads(response3_live.text)
        positie = 0
        for y in result3_live['data']:
            if 'rtmp' in y['attributes']['source'].keys():
                if y['attributes']['content_type'] == 'video/h264':
                    vid_id = y['id']
                    datum=(y['attributes']['source']['connected_at'])
                    url=(y['attributes']['source']['rtmp'])
                    title=datum

                    list_item = xbmcgui.ListItem(label=datum)
                    list_item.setInfo('video', {'title': title,
                                                'mediatype': 'video',
                                                'comment' : 'test1243555'})
                    list_item.setArt({'thumb': thumb, 'icon': thumb, 'fanart': thumb})
                    list_item.setProperty('IsPlayable', 'true')
                    is_folder = False
                    xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
            positie += 1
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.endOfDirectory(_handle)

def play_video(path):
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):

    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    xbmc.log(str(params), level=xbmc.LOGINFO);
    # Check the parameters passed to the plugin
    if params:
        try:
            zoekopdracht=params['zoek']
            if zoekopdracht == "nieuw":
                zoekopdracht = xbmcgui.Dialog().input("Geef een zoekopdracht op")
                if zoekopdracht == "":
                    zoekopdracht = "test"
                else:
                    f = open(history_file, 'a')
                    f.write(zoekopdracht+ "\n")
                    f.close()
            if zoekopdracht == "leeg":
                open(history_file, 'w').close()

            params['action']

            response_live = requests.get('https://api.kerkdienstgemist.nl/api/v1/search?query=' +quote(zoekopdracht)+ '&live=1',
                    auth = HTTPBasicAuth('app_v1', 'Y4KBuCTXm9GbkZfL'))

            # print request object
            result_live = json.loads(response_live.text)
            for x in result_live["data"]:
                link = x['relationships']['station']['links']['related']
                response2_live = requests.get(link,
                        auth = HTTPBasicAuth('app_v1', 'Y4KBuCTXm9GbkZfL'))
                result2_live = json.loads(response2_live.text)
                afbeelding_live.append(result2_live['data']['attributes']['image']['thumb'])
                kerk_live.append('Live '+result2_live['data']['attributes']['name'])
                opnames_live.append(result2_live['data']['relationships']['streams']['links']['related'])
                xbmcplugin.setPluginCategory(_handle, 'Kerkdienstgemist')
                xbmcplugin.setContent(_handle, 'videos')

            response = requests.get('https://api.kerkdienstgemist.nl/api/v1/search?query=' +quote(zoekopdracht)+ '&station=1',
                        auth = HTTPBasicAuth('app_v1', 'Y4KBuCTXm9GbkZfL'))
              
            result = json.loads(response.text)
            for x in result["data"]:
                link = x['relationships']['station']['links']['related']
                response2 = requests.get(link,
                        auth = HTTPBasicAuth('app_v1', 'Y4KBuCTXm9GbkZfL'))
                result2 = json.loads(response2.text)
                afbeelding.append(result2['data']['attributes']['image']['thumb'])
                kerk.append(result2['data']['attributes']['name'])
                opnames.append(result2['data']['relationships']['recordings']['links']['related'])

                xbmcplugin.setPluginCategory(_handle, 'Kerkdienstgemist')
                xbmcplugin.setContent(_handle, 'videos')
            xbmc.log(msg=zoekopdracht, level=xbmc.LOGINFO);
            if params['action'] == 'listing':
                # Display the list of videos in a provided category.
                if params['category'] == 'Opnames':
                    list_opnames(zoekopdracht)
                elif params['category'] == 'Live':
                    list_live(zoekopdracht)
                elif 'Live' in params['category']:
                    list_videos_live(params['category'], kerk_live)
                else:
                    list_videos(params['category'], kerk)
            elif params['action'] == 'play':
                # Play a video from a provided URL.
                play_video(params['video'])
            elif params['action'] == 'zoek':
                list_hoofdpagina(zoekopdracht)
            else:
                # If the provided paramstring does not contain a supported action
                # we raise an exception. This helps to catch coding errors,
                # e.g. typos in action names.
                raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
        except NameError:
            list_hoofdpagina(zoekopdracht)
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_hoofdpagina('test')


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
