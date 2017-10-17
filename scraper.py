import praw
from urllib.parse import urlparse
from datetime import datetime


def parse_rawurl(url):
    path = urlparse(url).path.split('/')
    id = path[4]
    return id


class ScrapedSubmission:

    # Submission object fields are fetched from API when they are addressed/called.
    def __init__(self, r, submission_id):

        self.post = r.submission(id=submission_id)

        self.title = self.post.title
        self.upvotes = str(self.post.ups)
        self.downvotes = str(self.post.downs)
        self.sub = self.post.subreddit.display_name
        self.selftext = self.post.selftext
        self.url = self.post.url

        self.created_at = datetime.fromtimestamp(
            int(self.post.created_utc)
        ).strftime('%Y-%m-%d %H:%M:%S UTC')

        self.post_url = 'https://www.reddit.com' + self.post.permalink

        if self.post.author:
            self.author = self.post.author.name
        else:
            self.author = '[deleted]'

        # We don't need to wait around, lets just get them now.
        
        #comments = self.get_comments()

    def get_comments(self):

        scraped = []

        comments = self.post.comments

        # expand MoreComments objects
        comments.replace_more()

        for comment in comments.list():
            scraped.append(ScrapedComment(comment))

        return scraped


class ScrapedComment:

    def __init__(self, commentobj):

        self.c = commentobj

        self.body = self.c.body
        self.upvotes = str(self.c.ups)

        self.created_at = datetime.fromtimestamp(
            int(self.c.created_utc)
        ).strftime('%Y-%m-%d %H:%M:%S UTC')

        self.permalink = "https://www.reddit.com" + self.c.permalink(fast=True)

        if hasattr(self.c.author, 'name'):
            self.username = self.c.author.name
        else:
            self.username = '[deleted]'
