import praw
import time
import operator
from prawcore.exceptions import NotFound

# OAuth credentials initially empty
app_client_id = ''
app_client_agent = ''
app_client_secret = ''

# Set this to the maximum number of latest users you want from each subreddit
MAX_USERS_PER_SUBREDDIT = 100

# Get credentials from auth.txt in the same directory
def import_credentials():
    try:
        f = open("auth.txt", "r")
    except OSError:
        return False
    creds = f.readlines()
    f.close()

    creds[0] = creds[0].strip() # App ID
    creds[1] = creds[1].strip() # App Secret
    creds[2] = creds[2].strip() # App User-Agent
    return creds

def is_redditor(user_name):
    reddit = praw.Reddit(client_id=app_client_id,
                         client_secret=app_client_secret,
                         user_agent=app_client_agent)

    try:
        reddit.redditor(user_name).id
    except NotFound:
        return False
    return True


def full_comment_and_submission_history(user_name):
    reddit = praw.Reddit(client_id=app_client_id,
                         client_secret=app_client_secret,
                         user_agent=app_client_agent)

    submission_history = reddit.redditor(user_name).submissions.top('all')
    comment_history = reddit.redditor(user_name).comments.top('all')

    submission_data = []

    for sub in submission_history:
        submission_data += [{"Title": sub.title,
                             "Date": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(sub.created_utc)),
                             "Content": sub.selftext,
                             "Subreddit": sub.subreddit.display_name}]

    for com in comment_history:
        submission_data += [{"Content": com.body,
                             "Title": "<<COMMENT>>",   # Comments don't inherently have a title so we assign one
                             "Subreddit": com.subreddit.display_name,
                             "Date": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(com.created_utc))}]

    return submission_data


def get_rank(element):
    return element[element.key]


def ranked_subreddits(user_history, max_count=1000):
    sub_count = {}
    for item in user_history:
        if item["Subreddit"] in sub_count.keys():
            sub_count[item["Subreddit"]] += 1
        else:
            sub_count.update({item["Subreddit"]: 1})

    return sorted(sub_count.items(), key=operator.itemgetter(1), reverse=True)[0:max_count]


# Get a list of up to 1000 of the latest contributors in a subreddit
def last_subreddit_users(sub_name, max_count=1000):
    author_list = []
    reddit = praw.Reddit(client_id=app_client_id,
                         client_secret=app_client_secret,
                         user_agent=app_client_agent)
    for comment in reddit.subreddit(sub_name).comments(limit=100):
        try:
            author_list += [comment.author.name]
        except AttributeError:
            continue

    return author_list


if __name__ == "__main__":

    users_list = []
    user_scores = {}
    top_subreddits = ()
    score: int = 0

    creds = import_credentials()

    # Set OAuth credentials
    if creds:
        app_client_id = creds[0]
        app_client_secret = creds[1]
        app_client_agent = creds[2]
    else:
        print("Please provide valid OAuth credentials in an auth.txt file")
        exit(0)

    original_user = input("Enter username (enter 'q' to quit): ")
    if original_user.upper().strip() == "Q":
        exit(0)

    print("Getting original user's top 5 subreddits...")

    # Original user's top 5 subreddits
    top_subreddits = ranked_subreddits(full_comment_and_submission_history(original_user), max_count=10)

    # Last 100 users in each of the top 5 subreddits
    sub_count = 1
    for sub_reddit in top_subreddits:
        print("Getting last 100 users in " + sub_reddit[0] + " (" + str(sub_count) + " of " + str(
            len(top_subreddits)) + ")...")
        sub_count += 1
        users_list = last_subreddit_users(sub_reddit[0], max_count=MAX_USERS_PER_SUBREDDIT)

        # Top 5 subreddits for each of the users in the current subreddit
        user_count = 1
        for user in users_list:
            print("Getting top subreddits for user " + str(user_count) + " of " + str(len(users_list)) + "...",
                  end="\r", flush=True)
            user_top_subreddits = ranked_subreddits(full_comment_and_submission_history(user), max_count=5)
            score = 1
            user_count += 1
            for comp_sub in user_top_subreddits:
                if comp_sub in top_subreddits:
                    score += 1
            if score > 1:
                user_scores.update({user: score})

        print ("\nMatched users so far: " + str(user_scores))

    matched_users = sorted(user_scores.items(), key=operator.itemgetter(1), reverse=True)

    print("\nUsers most like " + original_user + ":")
    for match in matched_users:
        print("User: " + match[0] + " | Score: " + str(match[1]))
