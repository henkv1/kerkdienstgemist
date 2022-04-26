# Module: main
# Author: Henk V
# Created on: 28.11.2014
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
import sys
from urllib.parse import urlencode, parse_qsl, quote
import xbmcgui
import xbmcplugin
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
    
zoekopdracht = xbmcplugin.getSetting(_handle, id='zoekopdracht')

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

def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urlencode(kwargs))

def list_hoofdpagina():
    xbmcplugin.setPluginCategory(_handle, 'Kerkdienstgemist')
    xbmcplugin.setContent(_handle, 'videos')
    category = 'Live'
    list_item = xbmcgui.ListItem(label=category)
    list_item.setInfo('video', {'title': category,
                                'mediatype': 'video'})
    url = get_url(action='listing', category=category)
    is_folder = True
    xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    category = 'Opnames'
    list_item = xbmcgui.ListItem(label=category)
    list_item.setInfo('video', {'title': category,
                                'mediatype': 'video'})
    url = get_url(action='listing', category=category)
    is_folder = True
    xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.endOfDirectory(_handle)

def list_live():
    xbmcplugin.setPluginCategory(_handle, 'Kerkdienstgemist')
    xbmcplugin.setContent(_handle, 'videos')
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
        url = get_url(action='listing', category=category)
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.endOfDirectory(_handle)

def list_opnames():
    xbmcplugin.setPluginCategory(_handle, 'Kerkdienstgemist')
    xbmcplugin.setContent(_handle, 'videos')

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
        url = get_url(action='listing', category=category)
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.endOfDirectory(_handle)


def list_videos(category):
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

def list_videos_live(category):
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
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'listing':
            # Display the list of videos in a provided category.
            if params['category'] == 'Opnames':
                list_opnames()
            elif params['category'] == 'Live':
                list_live()
            elif 'Live' in params['category']:
                list_videos_live(params['category'])
            else:
                list_videos(params['category'])
        elif params['action'] == 'play':
            # Play a video from a provided URL.
            play_video(params['video'])
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_hoofdpagina()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
