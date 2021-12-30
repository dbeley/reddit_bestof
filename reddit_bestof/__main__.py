"""
Create and send Reddit BestOf reports.
"""
import logging
import time
import argparse
import json
import locale
import requests
import praw
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from string import Template
from tqdm import tqdm
from typing import Tuple
from . import utils

logger = logging.getLogger()
logging.getLogger("praw").setLevel(logging.WARNING)
START_TIME = time.time()
MAX_POSTS_TO_EXTRACT = 3000


def get_pushshift_data(sub: str, min_timestamp: int, max_timestamp: int) -> list:
    url = f"https://api.pushshift.io/reddit/search/submission?&size=1000&subreddit={sub}&after={min_timestamp}&before={max_timestamp}"
    iter = 0
    while True:
        iter += 1
        time.sleep(3)
        req = requests.get(url)
        if req.status_code != 502 or iter > 5:
            break
    try:
        data = json.loads(req.text)
    except Exception as e:
        logger.error(e)
    return data["data"]


def get_pushshift_ids(
    sub: str, min_timestamp: int, max_timestamp: int, test: bool
) -> list:
    list_ids = []
    ids = get_pushshift_data(sub, min_timestamp, max_timestamp)
    while len(ids) > 0:
        for id in ids:
            list_ids.append(id["id"])
        logger.debug(f"New min timestamp = {ids[-1]['created_utc']}.")
        ids = get_pushshift_data(sub, ids[-1]["created_utc"], max_timestamp)
        if test:
            break
    return list_ids


def get_reddit_ids(
    reddit: praw.Reddit, sub: str, min_timestamp: int, max_timestamp: int, test: bool
) -> list:
    limit = 100 if test else MAX_POSTS_TO_EXTRACT
    posts = reddit.subreddit(sub).new(limit=limit)
    list_posts = [{"id": i.id, "timestamp": int(i.created_utc)} for i in posts]
    logger.debug(f"Posts extracted with praw API {len(list_posts)}")
    post_ids = [
        i["id"]
        for i in list_posts
        if i["timestamp"] >= min_timestamp and i["timestamp"] <= max_timestamp
    ]
    return post_ids


def get_timestamp_range(day: str) -> Tuple[int, int]:
    """Return the range of the report with a min and max timestamp.
    Example: for 2021-09-16, return the timestamp for 2021-09-15 21:00 and 2021-09-16 21:00
    """
    y, m, d = [int(x) for x in day.split("-", 3)]
    # needs to add 2 hours in order to have timestamp equivalent to the FR timezone.
    min_datetime = datetime(y, m, d, 23, 00) - timedelta(hours=24)
    return int(min_datetime.timestamp()), int(datetime(y, m, d, 23, 00).timestamp())


def get_data(reddit, post_ids: list) -> Tuple[list, list]:
    posts = []
    comments = []
    for id in tqdm(post_ids, dynamic_ncols=True):
        submission = reddit.submission(id)
        author = str(submission.author)
        if author != "None" and not submission.hidden and submission.is_robot_indexable:
            posts.append(
                {
                    "id": id,
                    "score": submission.score,
                    "author": utils.sanitize_username("/u/" + author),
                    "permalink": f"https://reddit.com{submission.permalink}",
                    "title": submission.title,
                    "timestamp": int(submission.created_utc),
                    "num_comments": submission.num_comments,
                }
            )
            submission.comments.replace_more(limit=None)
            for comment in submission.comments.list():
                author = str(comment.author)
                if author != "None":
                    body = utils.sanitize_comment_body(comment.body)
                    comments.append(
                        {
                            "id": comment.id,
                            "score": comment.score,
                            "author": utils.sanitize_username("/u/" + author),
                            "permalink": utils.sanitize_link(comment.permalink),
                            "body": body,
                            "parent": comment.parent_id,
                            "length": len(body),
                            "timestamp": int(submission.created_utc),
                        }
                    )
    return posts, comments


def redditconnect(config_section: str) -> praw.Reddit:
    user_agent = "python:script:reddit_bestof"
    reddit = praw.Reddit(config_section, user_agent=user_agent)
    return reddit


def get_env_title(post_env: dict, day: str) -> dict:
    y, m, d = [int(x) for x in day.split("-", 3)]
    date = datetime(y, m, d).strftime("%A %d %b %Y")
    return {
        "date": date,
        "title": post_env["best_comment_body"],
    }


def get_env_post(
    reddit: praw.Reddit, df_posts: pd.DataFrame, df_comments: pd.DataFrame
) -> dict:
    """Create stats from posts and comments."""
    number_total_posts = len(df_posts)
    number_total_comments = len(df_comments)
    number_unique_users = len(
        pd.unique(df_posts["author"].append(df_comments["author"], ignore_index=True))
    )
    best_post = utils.get_best_post(df_posts)
    commented_post = utils.get_commented_post(df_posts)
    best_comment = utils.get_best_comment(df_comments)
    worst_comment = utils.get_worst_comment(df_comments)
    discussed_comment = utils.get_discussed_comment(reddit, df_comments)
    amoureux_stat = utils.get_amoureux(df_comments)
    qualite_stat = utils.get_qualite(df_comments)
    poc_stat = utils.get_poc(df_comments)
    tartine_stat = utils.get_tartine(df_comments)
    capslock_stat = utils.get_capslock(df_comments)
    indecision_stat = utils.get_indecision(df_comments)
    jackpot_stat = utils.get_jackpot(df_comments)
    krach_stat = utils.get_krach(df_comments)

    return {
        "number_total_posts": number_total_posts,
        "number_total_comments": number_total_comments,
        "number_unique_users": number_unique_users,
        "best_post_author": best_post["best_post_author"],
        "best_post_score": best_post["best_post_score"],
        "best_post_title": best_post["best_post_title"],
        "best_post_link": best_post["best_post_link"],
        "best_post_id": best_post["best_post_id"],
        "commented_post_author": commented_post["commented_post_author"],
        "commented_post_comments": commented_post["commented_post_comments"],
        "commented_post_title": commented_post["commented_post_title"],
        "commented_post_link": commented_post["commented_post_link"],
        "commented_post_id": commented_post["commented_post_id"],
        "best_comment_author": best_comment["best_comment_author"],
        "best_comment_score": best_comment["best_comment_score"],
        "best_comment_body": best_comment["best_comment_body"],
        "best_comment_link": best_comment["best_comment_link"],
        "best_comment_id": best_comment["best_comment_id"],
        "worst_comment_author": worst_comment["worst_comment_author"],
        "worst_comment_score": worst_comment["worst_comment_score"],
        "worst_comment_body": worst_comment["worst_comment_body"],
        "worst_comment_link": worst_comment["worst_comment_link"],
        "worst_comment_id": worst_comment["worst_comment_id"],
        "discussed_comment_author": discussed_comment["discussed_comment_author"],
        "discussed_comment_answers": discussed_comment["discussed_comment_answers"],
        "discussed_comment_body": discussed_comment["discussed_comment_body"],
        "discussed_comment_link": discussed_comment["discussed_comment_link"],
        "discussed_comment_id": discussed_comment["discussed_comment_id"],
        "amoureux_author1": amoureux_stat["amoureux_author1"],
        "amoureux_author2": amoureux_stat["amoureux_author2"],
        "amoureux_score": amoureux_stat["amoureux_score"],
        "qualite_author": qualite_stat["qualite_author"],
        "qualite_score": qualite_stat["qualite_score"],
        "poc_author": poc_stat["poc_author"],
        "poc_score": poc_stat["poc_score"],
        "tartine_author": tartine_stat["tartine_author"],
        "tartine_score": tartine_stat["tartine_score"],
        "capslock_author": capslock_stat["capslock_author"],
        "capslock_score": capslock_stat["capslock_score"],
        "indecision_author": indecision_stat["indecision_author"],
        "indecision_score": indecision_stat["indecision_score"],
        "jackpot_author": jackpot_stat["jackpot_author"],
        "jackpot_score": jackpot_stat["jackpot_score"],
        "krach_author": krach_stat["krach_author"],
        "krach_score": krach_stat["krach_score"],
    }


def read_template(file: str) -> Template:
    with open(file, "r") as f:
        content = f.read()
    return Template(content)


def notify_winners(reddit: praw.Reddit, message: str, env_post: dict):
    logger.warning(
        f"Notifying winners. Don't do this if you're just testing the script!"
    )
    winning_comments = set(
        [
            env_post["best_comment_id"],
            env_post["worst_comment_id"],
            env_post["discussed_comment_id"],
        ]
    )
    for i in winning_comments:
        comment = reddit.comment(i)
        logger.info(f"Sending message to comment {i}.")
        comment.reply(message)


def main():
    args = parse_args()
    if not args.post_subreddit and not args.no_posting:
        raise ValueError(
            "You need to set -p/--post_subreddit. You can disable posting with --no-posting."
        )
    if not Path(args.template_file).is_file():
        raise FileNotFoundError(f"Template {args.template_file} does not exist.")
    if not args.no_posting:
        if not args.template_file_title:
            raise ValueError(
                f"You need to set -t/--template_file_title. You can disable posting with --no_posting."
            )
        if not Path(args.template_file_title).is_file():
            raise FileNotFoundError(
                f"Template {args.template_file_title} does not exist."
            )
        if args.notify_winners:
            if not args.template_file_message:
                raise ValueError(
                    f"You need to set -m/--template_file_message if you enable --notify_winners."
                )
            if not Path(args.template_file_message).is_file():
                raise FileNotFoundError(
                    f"Template {args.template_file_message} does not exist."
                )

    reddit = redditconnect("bot")
    locale.setlocale(locale.LC_TIME, "fr_FR.utf8")
    # pd.to_string() uses this option to truncate its output
    pd.options.display.max_colwidth = None

    report_day = datetime.now().strftime("%Y-%m-%d") if not args.day else args.day
    logger.info(f"Creating report for subreddit {args.subreddit} and day {report_day}.")
    min_timestamp, max_timestamp = get_timestamp_range(report_day)
    logger.debug(f"Extracting data between {min_timestamp} and {max_timestamp}.")

    # If a specific day is set, extract ids with pushshift, otherwise with praw
    if args.day:
        post_ids = get_pushshift_ids(
            args.subreddit, min_timestamp, max_timestamp, args.test
        )
    else:
        post_ids = get_reddit_ids(
            reddit, args.subreddit, min_timestamp, max_timestamp, args.test
        )

    if len(post_ids) == 0:
        raise ValueError(
            f"No posts were found on /r/{args.subreddit} for {report_day} (between {min_timestamp} and {max_timestamp})."
        )

    # Extract current data with praw
    posts, comments = get_data(reddit, post_ids)

    # Convert to pandas dataframe
    df_posts = pd.DataFrame(posts)
    df_comments = pd.DataFrame(comments)

    # Stats calculation + template evaluation
    env_post = get_env_post(reddit, df_posts, df_comments)
    formatted_message = read_template(args.template_file).safe_substitute(env_post)

    filename = f"{report_day}_{args.subreddit}_{int(START_TIME)}.txt"
    logger.info(f"Exporting formatted post to Exports/{filename}")
    Path("Exports").mkdir(parents=True, exist_ok=True)
    with open(f"Exports/{filename}", "w") as f:
        f.write(formatted_message)

    env_title = get_env_title(env_post, report_day)
    if not args.no_posting:
        post_title = read_template(args.template_file_title).safe_substitute(env_title)
        logger.info(
            f"Sending post to {args.post_subreddit}\nTitle: {post_title}\nContent: {formatted_message}"
        )
        submission = reddit.subreddit(args.post_subreddit).submit(
            title=post_title, selftext=formatted_message
        )
        if args.notify_winners and not args.test:
            env_message = {
                "reddit_bestof_url": f"https://reddit.com{submission.permalink}"
            }
            notify_winners_message = read_template(
                args.template_file_message
            ).safe_substitute(env_message)
            notify_winners(reddit, notify_winners_message, env_post)
    else:
        logger.info(f"Posting is disabled\nContent: {formatted_message}")

    logger.info("Runtime: %.2f seconds." % (time.time() - START_TIME))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create and send Reddit BestOf reports."
    )
    parser.add_argument(
        "--debug",
        help="Display debugging information",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    parser.add_argument(
        "-s",
        "--subreddit",
        help="Subreddit (required, without prefix, example: france)",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-f",
        "--template_file",
        help="Template file containing the content of the post (required)",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-t",
        "--template_file_title",
        help="Template file containing the title of the post (required if not using --no_posting)",
        type=str,
    )
    parser.add_argument(
        "-m",
        "--template_file_message",
        help="Template file containing the message for the winner's notification (required if --notify-winners is set)",
        type=str,
    )
    parser.add_argument(
        "-d",
        "--day",
        help="Report day in format YYYY-MM-DD (optional, if not set: current day)",
        type=str,
    )
    parser.add_argument(
        "-p",
        "--post_subreddit",
        help="Subreddit to send the formatted message to (without prefix, example: bestoffrance2)",
        type=str,
    )
    parser.add_argument(
        "--no_posting",
        help="Disable posting to Reddit",
        dest="no_posting",
        action="store_true",
    )
    parser.add_argument(
        "--test",
        help="Use a very small subset of data",
        dest="test",
        action="store_true",
    )
    parser.add_argument(
        "--notify_winners",
        help="Send a message to winners",
        dest="notify_winners",
        action="store_true",
    )
    parser.set_defaults(no_posting=False, test=False, notify_winners=False)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == "__main__":
    main()
