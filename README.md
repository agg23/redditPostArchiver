# redditPostArchiver  #

### A Subreddit Archiver for Reddit ###

**a script written in Python**

**Dependencies:** Either

 * [PRAW](https://github.com/praw-dev/praw), [snudown](https://github.com/reddit/snudown), Python 2.7 (Python 3.x not supported in official snudown branch)
 * [PRAW](https://github.com/praw-dev/praw), [Chid's snudown fork](https://github.com/chid/snudown), Python 3

## Quick Start ##

As a regular user, install praw:

    sudo pip install praw  

Snudown was recently removed from the pip database, it seems, so to install snudown:

    git clone https://github.com/reddit/snudown.git
    cd snudown
    sudo python setup.py install

Navigate to the folder with archive.py and run the script. An set of html files will be written into that same folder. To choose what subreddit is to be archived simply modify the configuration section in the script.

As of now, only posts and the associated comment threads can be archived. Saving a specific comment thread, starting with a comment, will be supported in the future.
