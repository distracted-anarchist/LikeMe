import operator
import time

import praw
from prawcore.exceptions import NotFound


# I removed all global variables. I would recommend avoiding them at all costs.


class Reddit:
    def __init__(self, app_client_id, app_client_agent, app_client_secret):
        self.reddit = praw.Reddit(client_id=app_client_id, client_secret=app_client_secret, user_agent=app_client_agent)

    def is_redditor(self, user_name):
        try:
            self.reddit.redditor(user_name).id
        except NotFound:
            return False
        return True

    def full_comment_and_submission_history(self, user_name):
        submission_history = self.reddit.redditor(user_name).submissions.top('all')
        comment_history = self.reddit.redditor(user_name).comments.top('all')

        # Okay, maybe this is a little silly, but I like list comprehensions
        submission_data = [[{"Title": sub.title,
                             "Date": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(sub.created_utc)),
                             "Content": sub.selftext, "Subreddit": sub.subreddit.display_name}] for sub in
                           submission_history] + [[{"Content": com.body, "Title": "<<COMMENT>>",
                                                    "Subreddit": com.subreddit.display_name,
                                                    "Date": time.strftime('%Y-%m-%d %H:%M:%S',
                                                                          time.gmtime(com.created_utc))}] for com in
                                                  comment_history]
        # Comments don't inherently have a title so we assign one
        return submission_data

    def ranked_subreddits(self, user_history, max_count=1000):
        sub_count = {}
        for item in user_history:
            if item["Subreddit"] in sub_count.keys():
                sub_count[item["Subreddit"]] += 1
            else:
                sub_count.update({item["Subreddit"]: 1})

        return sorted(sub_count.items(), key=operator.itemgetter(1), reverse=True)[0:max_count]

    # Get a list of up to 1000 of the latest contributors in a subreddit
    def last_subreddit_users(self, sub_name, max_count=1000):
        author_list = []
        for comment in self.reddit.subreddit(sub_name).comments(limit=100):
            try:
                author_list += [comment.author.name]
            except AttributeError:
                continue

        return author_list
