
import discord
from datetime import datetime
import xml.etree.ElementTree as ET #xml parser
import requests
import time
import rss #my rss module
import asyncio
import sys

tokenPath = './'
if len(sys.argv) >= 2:
    tokenPath = sys.argv[1] + '/'

#constants
DISCORD_TOKEN = ''
BUZZSPROUT_TOKEN = ''
with open(tokenPath + 'discord_token.txt', 'r') as f:
    DISCORD_TOKEN = f.read().rstrip()
with open(tokenPath + 'buzzsprout_token.txt', 'r') as f:
    BUZZSPROUT_TOKEN = f.read().rstrip()

LOG_FILE = 'village-bot.log'
BLOG_URL = 'http://www.villagersonline.com/feed'
BUZZSPROUT_URL = f'https://www.buzzsprout.com/api/11123/episodes.json?api_token={BUZZSPROUT_TOKEN}'

#setup other stuff here
isReady = False

lastCheck = datetime.now()

headerDate = rss.getHeaderDate(lastCheck)



#not used yet
sermonPosted = True #checks if this weeks sermon has been posted yet

blogChannel = None #getChannel(client, 'villager-writing')
sermonChannel = None #getChannel(client, 'sermons')

#utility functions
def getChannel(client, channelName):
    guild = client.guilds[0]
    for c in guild.channels:
        if c.name == channelName:
            return c
    return None

async def check(blogChannel, sermonChannel):
    lastCheck = datetime.utcnow()
    log('Init', "'lastCheck' initialized to " + lastCheck.isoformat())
    while True:
        await asyncio.sleep(3600)
        log('Note', 'Checking blog...')
        try:
            blog = rss.getModifiedSinceRSS(BLOG_URL, lastCheck)
##            sermon = rss.getModifiedSinceJSON(BUZZSPROUT_URL, lastCheck)
            newCheckDate = datetime.utcnow()
            #log('Note', 'Done checking')
            if blog.code == 200:
                logl('Note', 'Found ' + str(len(blog.data)) + ' new posts',
                     blog.data)
                for link in blog.data:
                    await blogChannel.send(link)
            elif blog.code == 304:
                log('Note', 'No new posts')
            else:
                log('Warning', 'Blog: ' + str(blog.code) + ' ' + blog.reason)
        except:
            log('Error', 'Check internet connenction')
        
##        if sermon.code == 200:
##            sermonLink = sermon.data[i]['audio_url'][:-4]
##            log('Note', 'Found ' + str(len(sermons)) + ' new sermons',
##                sermonLink)
##            await sermonChannel.send(sermonLink)
##            sermons = []
##            for i in range(len(sermon.data)):
##                if lastCheck < datetime.fromisoformat(sermon.data[i]['published_at']):
##                    sermons.append(sermon.data[i]['audio_url'][:-4])
##                    await sermonChannel.send(sermons[-1])
##                else:
##                    break
##            logl('Note', 'Found ' + str(len(sermons)) + ' new sermons',
##                 sermons)
##        elif sermon.code == 304:
##            log('Note', 'No new sermons')
##        else:
##            log('Warning', 'Sermon: ' + str(sermon.code) + ' ' + sermon.reason)
        lastCheck = newCheckDate


def log(notice, s, *args):
    t = datetime.now().isoformat(sep=' ') + ' ' + notice + ': '
    space = len(t)
    with open(LOG_FILE, 'a') as f:
        f.write(t + s + '\n')
        for arg in args:
            f.write((' '*space) + arg + '\n')
def logl(notice, s, l):
    t = datetime.now().isoformat(sep=' ') + ' ' + notice + ': '
    space = len(t)
    with open(LOG_FILE, 'a') as f:
        f.write(t + s + '\n')
        for line in l:
            f.write((' '*space) + line + '\n')


client = discord.Client()

@client.event
async def on_ready():
    global isReady
    log('Note', "'on_ready()' called")
    if not isReady:
        log('Init', 'Logged in as ' + client.user.name + '#'
            + str(client.user.discriminator), str(client.user.id))
        blogChannel = client.get_channel(725089770858086500)
        if blogChannel is None:
            log('Error', "'blogChannel is 'None'")
        sermonChannel = client.get_channel(725048672789725286)
        if sermonChannel is None:
            log('Error', "'sermonChannel is 'None'")
        isReady = True
        await check(blogChannel, sermonChannel)
    else:
        log('Reconnect', "'on_ready()' was called again")
        blogChannel = client.get_channel(725089770858086500)
        if blogChannel is None:
            log('Error', "'blogChannel is 'None'")
        sermonChannel = client.get_channel(725048672789725286)
        if sermonChannel is None:
            log('Error', "'sermonChannel is 'None'")


client.run(DISCORD_TOKEN)



