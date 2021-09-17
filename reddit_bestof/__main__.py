"""
Create and send Reddit BestOf reports.
"""
import logging
import time
import argparse
import requests
import praw
import json
import locale
import pandas as pd
from datetime import datetime
from pathlib import Path
from . import stats

logger = logging.getLogger()
logging.getLogger("praw").setLevel(logging.WARNING)
START_TIME = time.time()


def get_pushshift_posts(sub: str, min_timestamp: int, max_timestamp: int) -> list:
    url = (
        "https://api.pushshift.io/reddit/search/submission?&size=1000"
        + "&subreddit="
        + str(sub)
        + "&after="
        + str(min_timestamp)
        + "&before="
        + str(max_timestamp)
    )
    req = requests.get(url)
    data = json.loads(req.text)
    return data["data"]


def get_pushshift_comments(sub: str, min_timestamp: int, max_timestamp: int) -> list:
    url = (
        "https://api.pushshift.io/reddit/search/comment?&size=1000"
        + "&subreddit="
        + str(sub)
        + "&after="
        + str(min_timestamp)
        + "&before="
        + str(max_timestamp)
    )
    req = requests.get(url)
    data = json.loads(req.text)
    return data["data"]


def get_bestof_timestamp(day: str) -> (int, int):
    """Return the range of the report with a min and max timestamp.
    Example: for 2021-09-16, return the timestamp for 2021-09-15 21:00 and 2021-09-16 21:00
    """
    y, m, d = [int(x) for x in day.split("-", 3)]
    # needs to add 2 hours in order to have timestamp equivalent to the FR timezone.
    return int(datetime(y - 1, m, d, 22, 00).timestamp()), int(
        datetime(y - 1, m, d, 23, 00).timestamp()
    )
    # return int(datetime(y, m, d - 1, 23, 00).timestamp()), int(
    #     datetime(y, m, d, 23, 00).timestamp()
    # )


def get_post_data(reddit, post_ids: list) -> list:
    posts = []
    for id in post_ids:
        submission = reddit.submission(id)
        author = str(submission.author)
        if author != "None":
            posts.append(
                {
                    "score": submission.score,
                    "author": author,
                    "permalink": f"https://reddit.com{submission.permalink}",
                    "title": submission.title,
                    # "Hidden": submission.hidden,
                    # "Archived": submission.archived,
                }
            )
    return posts


def get_comment_data(reddit, comment_ids: list) -> list:
    comments = []
    for id in comment_ids:
        comment = reddit.comment(id)
        author = str(comment.author)
        if author != "None":
            comments.append(
                {
                    "id": comment.id,
                    "score": comment.score,
                    "author": author,
                    "permalink": f"https://reddit.com{comment.permalink}",
                    "body": comment.body,
                    "parent": comment.parent_id,
                    "length": len(comment.body),
                }
            )
    return comments


def redditconnect(config_section: str):
    user_agent = "python:script:reddit_bestof"
    reddit = praw.Reddit(config_section, user_agent=user_agent)
    return reddit


def format_title(template: str, title: str, day: str) -> str:
    y, m, d = [int(x) for x in day.split("-", 3)]
    date = datetime(y, m, d).strftime("%A %d %b. %Y")
    return eval(template)


def format_report(template: str, post_data: list, comment_data: list) -> str:
    """Create stats from post_data and comment_data.
    Replace variables in template
    Available tokens:
    - number_total_posts
    - number_total_comments
    - number_unique_users
    - best_post_author
    - best_post_score
    - best_post_title
    - best_post_link
    - best_comment_author
    - best_comment_score
    - best_comment_body
    - best_comment_link
    - worst_comment_author
    - worst_comment_score
    - worst_comment_body
    - worst_comment_link
    - discussed_comment_author
    - discussed_comment_answers
    - discussed_comment_body
    - discussed_comment_link
    - amoureux_author1
    - amoureux_author2
    - amoureux_score
    - qualite_author
    - qualite_score
    - poc_author
    - poc_score
    - tartine_author
    - tartine_score
    - capslock_author
    - capslock_score
    - indecision_author
    - indecision_score
    - jackpot_author
    - jackpost_score
    - krach_author
    - krach_score
    """
    number_total_posts = len(post_data)
    number_total_comments = len(comment_data)

    df_posts = pd.DataFrame(post_data)
    df_comments = pd.DataFrame(comment_data)
    number_unique_users = len(
        pd.unique(df_posts["author"].append(df_comments["author"], ignore_index=True))
    )
    (
        best_post_author,
        best_post_score,
        best_post_title,
        best_post_link,
    ) = stats.get_best_post(df_posts)
    (
        best_comment_author,
        best_comment_score,
        best_comment_body,
        best_comment_link,
    ) = stats.get_best_comment(df_comments)
    (
        worst_comment_author,
        worst_comment_score,
        worst_comment_body,
        worst_comment_link,
    ) = stats.get_worst_comment(df_comments)
    (
        discussed_comment_author,
        discussed_comment_answers,
        discussed_comment_body,
        discussed_comment_link,
    ) = stats.get_discussed_comment(df_comments)
    amoureux_author1, amoureux_author2, amoureux_score = stats.get_amoureux(df_comments)
    qualite_author, qualite_score = stats.get_qualite(df_comments)
    poc_author, poc_score = stats.get_poc(df_comments)
    tartine_author, tartine_score = stats.get_tartine(df_comments)
    capslock_author, capslock_score = stats.get_capslock(df_comments)
    indecision_author, indecision_score = stats.get_indecision(df_comments)
    jackpot_author, jackpot_score = stats.get_jackpot(df_comments)
    krach_author, krach_score = stats.get_krach(df_comments)

    formatted_message = eval(template)
    return formatted_message, best_post_title


def read_template(file: str) -> str:
    if not Path(file).is_file():
        raise ValueError(f"File {file} does not exist.")
    with open(file, "r") as f:
        content = f.read()
    return content


def main():
    args = parse_args()
    reddit = redditconnect("bot")
    locale.setlocale(locale.LC_TIME, "fr_FR.utf8")
    report_day = datetime.now().strftime("%Y-%m-%d") if not args.day else args.day
    logger.info(
        f"Creating report for subreddit {args.report_subreddit} and day {report_day}."
    )
    min_timestamp, max_timestamp = get_bestof_timestamp(report_day)
    logger.debug(f"Extracting data between {min_timestamp} and {max_timestamp}.")

    template = read_template(args.template_file)
    template_title = read_template(args.template_file_title)

    post_ids = []
    posts = get_pushshift_posts(args.report_subreddit, min_timestamp, max_timestamp)
    while len(posts) > 0:
        for submission in posts:
            post_ids.append(submission["id"])
        logger.debug(f"Post timestamp = {posts[-1]['created_utc']}")
        posts = get_pushshift_posts(
            args.report_subreddit, posts[-1]["created_utc"], max_timestamp
        )
    comment_ids = []
    comments = get_pushshift_comments(
        args.report_subreddit, min_timestamp, max_timestamp
    )
    while len(comments) > 0:
        for submission in comments:
            comment_ids.append(submission["id"])
        logger.debug(f"Comment timestamp = {comments[-1]['created_utc']}")
        comments = get_pushshift_comments(
            args.report_subreddit, comments[-1]["created_utc"], max_timestamp
        )
    logger.debug(
        f"Successfully extracted {len(post_ids)} post IDs and {len(comment_ids)} comment IDs for day {report_day}."
    )

    post_data = get_post_data(reddit, post_ids)
    comment_data = get_comment_data(reddit, comment_ids)
    formatted_message, title = format_report(template, post_data, comment_data)
    breakpoint()

    post_title = format_title(template_title, title, report_day)
    if args.no_posting:
        logger.info(
            f"Posting is disabled. Title: {post_title}. Content: {formatted_message}."
        )
    elif not args.post_subreddit:
        logger.info(
            f"Post Subreddit not set (use the -p argument). Title: {post_title}. Content: {formatted_message}."
        )
    else:
        logger.info(
            f"Sending post to {args.post_subreddit}. Title: {post_title}. Content: {formatted_message}."
        )
        reddit.subreddit(args.post_subreddit).submit(title=post_title)

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
        "--report_subreddit",
        help="Subreddit (required, without prefix, example: france).",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-f",
        "--template_file",
        help="Template file containing the content of the post (required).",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-t",
        "--template_file_title",
        help="Template file containing the title of the post (required).",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-d",
        "--day",
        help="Report day in format YYYY-MM-DD (default: current day).",
        type=str,
    )
    parser.add_argument(
        "-p",
        "--post_subreddit",
        help="Subreddit to send the formatted message to (without prefix, example: bestoffrance2).",
        type=str,
    )
    parser.add_argument(
        "--no_posting",
        help="Disable posting to Reddit.",
        dest="no_posting",
        action="store_true",
    )
    parser.set_defaults(no_posting=False)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == "__main__":
    main()
