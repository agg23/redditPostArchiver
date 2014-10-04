#!/usr/bin/env python
# -*- coding: utf-8 -*-

import praw
import snudown
import datetime
import time
import re
import sys
from requests.exceptions import HTTPError

""" 
Customization Configuration

"""

subreddit = '[Put subreddit name here (i.e. technology)]'

login = True;
username = '[Reddit username]'
password = '[Reddit password]'

startingPostID = '[Starting Reddit Post ID]'

# Path to which to output the file #
outputFilePath='./posts/'
# The Path to the stylesheet, relative to where the html file will be stored #
pathToCSS='css/style.css'

batchTitles = []
batchIDS = []
batchDates = []
batchUsernames = []
batchUsernameURLs = []

currentIndex = 0

"""
Subreddit Archiver
By Adam Gastineau (original source from Samuel Johnson Stoever)
"""

monthsList = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']


def writeHeader(posttitle, htmlFile):
    htmlFile.write('<!DOCTYPE html>\n<html>\n<head>\n')
    htmlFile.write('\t<meta charset="utf-8"/>\n')
    htmlFile.write('\t<link type="text/css" rel="stylesheet" href="../' + pathToCSS +'"/>\n')
    htmlFile.write('\t<title>' + posttitle + '</title>\n')
    htmlFile.write('</head>\n<body>\n')

def parsePost(postObject, htmlFile):
    writeHeader(fixUnicode(postObject.title), htmlFile)
    postObject.replace_more_comments()
    postAuthorName = ''
    postAuthorExists = 0
    try:
        postAuthorName = fixUnicode(postObject.author.name)
        postAuthorExists = 1
    except AttributeError:
        postAuthorExists = 0
    htmlFile.write('<div class="title">\n')
    if postObject.is_self:
        # The post is a self post
        htmlFile.write(fixUnicode(postObject.title))
        htmlFile.write('\n<br/><strong>')
    else:
        # The post is a link post
        htmlFile.write('<a id="postlink" href="' + fixUnicode(postObject.url))
        htmlFile.write('">')
        htmlFile.write(fixUnicode(postObject.title))
        htmlFile.write('</a>\n<br/><strong>')
    if postAuthorExists:
        htmlFile.write('Posted by <a id="userlink" href="' + fixUnicode(postObject.author._url))
        htmlFile.write('">')
        htmlFile.write(postAuthorName)
        htmlFile.write('</a>. </strong><em>')
    else:
        htmlFile.write('Posted by [Deleted]. </strong><em>')
    htmlFile.write('Posted at ')
    postDate = time.gmtime(postObject.created_utc)
    htmlFile.write(str(postDate.tm_hour) + ':')
    htmlFile.write(str(postDate.tm_min) + ' UTC on ')
    htmlFile.write(monthsList[postDate.tm_mon-1] + ' ')
    htmlFile.write(str(postDate.tm_mday) + ', ' + str(postDate.tm_year))
    htmlFile.write('. ' + str(postObject.ups - postObject.downs))
    if postObject.is_self:
        htmlFile.write(' Points. </em><em>(self.<a id="selfLink" href="')
    else:
        htmlFile.write(' Points. </em><em>(<a id="selfLink" href="')
    htmlFile.write(postObject.subreddit._url)
    htmlFile.write('">' + postObject.subreddit.display_name)
    if postObject.is_self:
        htmlFile.write('</a>)</em><em>')
    else:
        htmlFile.write('</a> Subreddit)</em><em>')
    htmlFile.write(' (<a id="postpermalink" href="')
    htmlFile.write(fixUnicode(postObject.permalink))
    htmlFile.write('">Permalink</a>)</em>\n')
    if postObject.is_self:
        htmlFile.write('<div class="post">\n')
        htmlFile.write(snudown.markdown(fixMarkdown(postObject.selftext)))
        htmlFile.write('</div>\n')
    else:
        htmlFile.write('<div class="post">\n<p>\n')
        htmlFile.write(postObject.url)
        htmlFile.write('</p>\n</div>\n')
    htmlFile.write('</div>\n')
    for comment in postObject._comments:
        parseComment(comment, postAuthorName, postAuthorExists, htmlFile, True)
    htmlFile.write('<hr id="footerhr">\n')
    htmlFile.write('<div id="footer"><em>Archived on ')
    htmlFile.write(str(datetime.datetime.utcnow()))
    htmlFile.write(' UTC</em></div>')
    htmlFile.write('\n\n</body>\n</html>\n')
    #Done
def parseComment(redditComment, postAuthorName, postAuthorExists, htmlFile, isRoot=True):
    commentAuthorName = ''
    commentAuthorExists = 0
    try:
        commentAuthorName = fixUnicode(redditComment.author.name)
        commentAuthorExists = 1
    except AttributeError:
        commentAuthorExists = 0
    if isRoot:
        htmlFile.write('<div id="' + str(redditComment.id))
        htmlFile.write('" class="comment">\n')
    else:
        htmlFile.write('<div id="' + str(redditComment.id)) 
        htmlFile.write('" class="comment" style="margin-bottom:10px;margin-left:0px;">\n')
    htmlFile.write('<div class="commentinfo">\n')
    if commentAuthorExists:
        if postAuthorExists and postAuthorName == commentAuthorName:
            htmlFile.write('<a href="' + redditComment.author._url)
            htmlFile.write('" class="postOP-comment">' + commentAuthorName + '</a> <em>')
        else:
            htmlFile.write('<a href="' + redditComment.author._url)
            htmlFile.write('">' + commentAuthorName + '</a> <em>')
    else:
        htmlFile.write('<strong>[Deleted]</strong> <em>')
    htmlFile.write(str(redditComment.ups - redditComment.downs))
    htmlFile.write(' Points </em><em>')
    htmlFile.write('Posted at ')
    postDate = time.gmtime(redditComment.created_utc)
    htmlFile.write(str(postDate.tm_hour) + ':')
    htmlFile.write(str(postDate.tm_min) + ' UTC on ')
    htmlFile.write(monthsList[postDate.tm_mon-1] + ' ')
    htmlFile.write(str(postDate.tm_mday) + ', ' + str(postDate.tm_year))
    htmlFile.write('</em></div>\n')
    htmlFile.write(snudown.markdown(fixMarkdown(redditComment.body)))
    for reply in redditComment._replies:
        parseComment(reply, postAuthorName, postAuthorExists, htmlFile, False)
    htmlFile.write('</div>\n')
    #Done
def fixMarkdown(markdown):
    newMarkdown = markdown.encode('utf8')
    return re.sub('\&gt;', '>', newMarkdown)
def fixUnicode(text):
    return text.encode('utf8')
def createPost(post):
    finalFilePath = outputFilePath + post.id + '.html'
    htmlFile = open(finalFilePath,'w')
    parsePost(post, htmlFile)
    htmlFile.close()

def writeIndexHeader(htmlFile):
    htmlFile.write('<!DOCTYPE html>\n<html>\n<head>\n')
    htmlFile.write('\t<meta charset="utf-8"/>\n')
    htmlFile.write('\t<link type="text/css" rel="stylesheet" href="css/index.css"/>\n')
    fileNumber = '';
    if(currentIndex != 0):
        fileNumber = ' - Page ' + str(currentIndex+1)
    title = subreddit + ' Index' + fileNumber;
    htmlFile.write('\t<title>' + title + '</title>\n')
    htmlFile.write('</head>\n<body>\n')
    htmlFile.write('<div class="title">' + title + '</div>')

def createIndex():
    fileNumber = ''
    if(currentIndex != 0):
        fileNumber = str(currentIndex)
    finalFilePath = './' + 'index' + fileNumber + '.html'
    htmlFile = open(finalFilePath,'w')
    writeIndexHeader(htmlFile)
    htmlFile.write('<div class="postlinks">')
    i = 0;
    for title in batchTitles:
        htmlFile.write('<div class="link">')
        htmlFile.write('<a href="' + outputFilePath + batchIDS[i] + '.html">' + title + '</a><br>')
        url = ''
        if(batchUsernameURLs[i] != ''):
            url = 'href="' + batchUsernameURLs[i] + '"'
        htmlFile.write('<a class="username" ' + url + '>By ' + batchUsernames[i] + '</a>')
        htmlFile.write('<div class="date">')
        htmlFile.write('Posted at ')
        postDate = batchDates[i]
        htmlFile.write(str(postDate.tm_hour) + ':')
        htmlFile.write(str(postDate.tm_min) + ' UTC on ')
        htmlFile.write(monthsList[postDate.tm_mon-1] + ' ')
        htmlFile.write(str(postDate.tm_mday) + ', ' + str(postDate.tm_year))
        htmlFile.write('</div>')
        htmlFile.write('</div>')
        i = i+1
    htmlFile.write('</div>')
    htmlFile.write('<div class="nav">')
    if(currentIndex != 0):
        index = ''
        if(currentIndex-1 != 0):
            index = str(currentIndex-1)
        htmlFile.write('<a href="' + './index' + index + '.html">Prev</a>')
    htmlFile.write('<a href="' + './index' + str(currentIndex+1) + '.html">Next</a>')
    htmlFile.write('</div>')
    htmlFile.write('\n\n</body>\n</html>\n')
    htmlFile.close()

# End Function Definitions


r = praw.Reddit(user_agent='Subreddit Archiver, version 0.1 by agg23')
if login:
    r.login(username, password)
try:
    submissions = r.get_subreddit(subreddit).get_new(limit=None, params={'after': startingPostID});
    i = 0;
    for x in submissions:
        i = i+1;
        createPost(x);
        print('Downloading ' + fixUnicode(x.id))
        batchTitles.append(fixUnicode(x.title));
        batchIDS.append(fixUnicode(x.id));
        batchDates.append(time.gmtime(x.created_utc));
        postAuthorName = ''
        postAuthorURL = ''
        try:
            postAuthorName = fixUnicode(x.author.name)
            postAuthorURL = fixUnicode(x.author._url)
        except AttributeError:
            postAuthorName = '[Deleted]'
        batchUsernames.append(postAuthorName);
        batchUsernameURLs.append(postAuthorURL);
        if(i == 25):
            i = 0
            print('Building index ' + str(currentIndex))
            createIndex()
            batchTitles = []
            batchIDS = []
            batchDates = []
            batchUsernames = []
            batchUsernameURLs = []
            currentIndex = currentIndex+1

        time.sleep(2)
    createIndex()
except HTTPError: 
    print('Unable to Archive Subreddit: Invalid Subreddit or Log In Required (see line 157 of script)')
##Done
