import operator
import sys

from Reddit import Reddit

# I removed all global variables. I would recommend avoiding them at all costs.


def import_credentials(authFileName):  # This is a static function so I thought it made sense to put it into the main file.
    try:
        with open(authFileName,
                  "r") as authFile:  # The with statement handles the opening and closing of a file for you
            creds = authFile.readline()
            creds = [cred.strip() for cred in creds]
            # Here you are doing a simple operation on each of the elements of a list.
            # A list comprehension is a great and efficient way of doing this.
            return creds
    except OSError:
        return False


def main():
    # Just a quick note. I prefer camelCase over underscores so that is what I used for the variable names I changed.
    authFile = "auth.txt"

    creds = import_credentials(authFile)
    if creds is False or len(creds) < 3:
        print("The OAuth file is not valid, or it does not exist.")
        print("Please provide valid OAuth credentials in ", authFile, ".", sep="")
        sys.exit()  # sys.exit() is I believe the more pythonic way of doing this.
        # sys.exit() is meant more for programs where as exit(0) is meant for the interactive console. I think.
    else:
        reddit = Reddit(*creds)
        # By creating a Reddit object we don't need to worry about passing credentials when we want to use the,

    inital_user = input("Enter username (enter 'q' to quit): ")
    if inital_user == "q":  # Why don't you just do this?
        sys.exit()

    print("Getting original user's top 5 subreddits...")
    # Original user's top 5 subreddits
    top_subreddits = reddit.ranked_subreddits(reddit.full_comment_and_submission_history(inital_user), max_count=10)

    user_scores = {}
    # Set this to the maximum number of latest users you want from each subreddit
    MAX_USERS_PER_SUBREDDIT = 100
    # Last 100 users in each of the top 5 subreddits
    for sub_count, sub_reddit in enumerate(top_subreddits): # enumerate gets you a iterable and an index variable
        # In this case sub_count was just the index+1
        print("Getting last 100 users in " + sub_reddit[0] + " (" + str(sub_count+1) + " of " + str(
            len(top_subreddits)) + ")...")
        users_list = reddit.last_subreddit_users(sub_reddit[0], max_count=MAX_USERS_PER_SUBREDDIT)

        # Top 5 subreddits for each of the users in the current subreddit
        user_count = 1
        for user in users_list:
            print("Getting top subreddits for user " + str(user_count) + " of " + str(len(users_list)) + "...",
                  end="\r", flush=True)
            user_top_subreddits = reddit.ranked_subreddits(reddit.full_comment_and_submission_history(user),
                                                           max_count=5)
            score = 1
            user_count += 1
            for comp_sub in user_top_subreddits:
                if comp_sub in top_subreddits:
                    score += 1
            if score > 1:
                user_scores.update({user: score})

        print("\nMatched users so far: " + str(user_scores))

    matched_users = sorted(user_scores.items(), key=operator.itemgetter(1), reverse=True)

    print("\nUsers most like " + inital_user + ":")
    for match in matched_users:
        print("User: " + match[0] + " | Score: " + str(match[1]))


if __name__ == '__main__': main()
