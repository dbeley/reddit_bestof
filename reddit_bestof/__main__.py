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
from datetime import datetime, timedelta
from pathlib import Path
from tqdm import tqdm
from string import Template
from . import utils

logger = logging.getLogger()
logging.getLogger("praw").setLevel(logging.WARNING)
START_TIME = time.time()
VALID_PUSHSHIFT_TYPES = ["submission", "comment"]


def get_pushshift_data(
    type: str, sub: str, min_timestamp: int, max_timestamp: int
) -> list:
    if type not in VALID_PUSHSHIFT_TYPES:
        raise ValueError(
            f"{type} is not a valid pushshift type. Valid values = {VALID_PUSHSHIFT_TYPES}."
        )
    url = f"https://api.pushshift.io/reddit/search/{type}?&size=1000&subreddit={sub}&after={min_timestamp}&before={max_timestamp}"
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
    type: str, sub: str, min_timestamp: int, max_timestamp: int, test: bool
) -> list:
    list_ids = []
    ids = get_pushshift_data(type, sub, min_timestamp, max_timestamp)
    while len(ids) > 0:
        for id in ids:
            list_ids.append(id["id"])
        logger.debug(f"New min timestamp = {ids[-1]['created_utc']}.")
        ids = get_pushshift_data(type, sub, ids[-1]["created_utc"], max_timestamp)
        if test:
            break
    return list_ids


def get_timestamp_range(day: str) -> (int, int):
    """Return the range of the report with a min and max timestamp.
    Example: for 2021-09-16, return the timestamp for 2021-09-15 21:00 and 2021-09-16 21:00
    """
    y, m, d = [int(x) for x in day.split("-", 3)]
    # needs to add 2 hours in order to have timestamp equivalent to the FR timezone.
    min_datetime = datetime(y, m, d, 23, 00) - timedelta(hours=24)
    return int(min_datetime.timestamp()), int(datetime(y, m, d, 23, 00).timestamp())


def get_data(reddit, post_ids: list) -> (list, list):
    posts = []
    comments = []
    logger.info("Extracting posts")
    for id in tqdm(post_ids, dynamic_ncols=True):
        submission = reddit.submission(id)
        author = str(submission.author)
        if author != "None" and not submission.hidden and submission.is_robot_indexable:
            posts.append(
                {
                    "score": submission.score,
                    "author": author,
                    "permalink": f"https://reddit.com{submission.permalink}",
                    "title": submission.title,
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
                            "author": author,
                            "permalink": f"https://reddit.com{comment.permalink}",
                            "body": body,
                            "parent": comment.parent_id,
                            "length": len(body),
                        }
                    )
    return posts, comments


def redditconnect(config_section: str):
    user_agent = "python:script:reddit_bestof"
    reddit = praw.Reddit(config_section, user_agent=user_agent)
    return reddit


def format_title(template: Template, title: str, day: str) -> str:
    y, m, d = [int(x) for x in day.split("-", 3)]
    date = datetime(y, m, d).strftime("%A %d %b %Y")
    env = {"title": title, "date": date}
    return template.safe_substitute(env)


def format_report(
    reddit, template: Template, df_posts: pd.DataFrame, df_comments: pd.DataFrame
) -> str:
    """Create stats from posts and comments."""
    number_total_posts = len(df_posts)
    number_total_comments = len(df_comments)
    number_unique_users = len(
        pd.unique(df_posts["author"].append(df_comments["author"], ignore_index=True))
    )
    (
        best_post_author,
        best_post_score,
        best_post_title,
        best_post_link,
    ) = utils.get_best_post(df_posts)
    (
        best_comment_author,
        best_comment_score,
        best_comment_body,
        best_comment_link,
    ) = utils.get_best_comment(df_comments)
    (
        worst_comment_author,
        worst_comment_score,
        worst_comment_body,
        worst_comment_link,
    ) = utils.get_worst_comment(df_comments)
    (
        discussed_comment_author,
        discussed_comment_answers,
        discussed_comment_body,
        discussed_comment_link,
    ) = utils.get_discussed_comment(reddit, df_comments)
    amoureux_author1, amoureux_author2, amoureux_score = utils.get_amoureux(df_comments)
    qualite_author, qualite_score = utils.get_qualite(df_comments)
    poc_author, poc_score = utils.get_poc(df_comments)
    tartine_author, tartine_score = utils.get_tartine(df_comments)
    capslock_author, capslock_score = utils.get_capslock(df_comments)
    indecision_author, indecision_score = utils.get_indecision(df_comments)
    jackpot_author, jackpot_score = utils.get_jackpot(df_comments)
    krach_author, krach_score = utils.get_krach(df_comments)

    env = {
        "number_total_posts": number_total_posts,
        "number_total_comments": number_total_comments,
        "number_unique_users": number_unique_users,
        "best_post_author": best_post_author,
        "best_post_score": best_post_score,
        "best_post_title": best_post_title,
        "best_post_link": best_post_link,
        "best_comment_author": best_comment_author,
        "best_comment_score": best_comment_score,
        "best_comment_body": best_comment_body,
        "best_comment_link": best_comment_link,
        "worst_comment_author": worst_comment_author,
        "worst_comment_score": worst_comment_score,
        "worst_comment_body": worst_comment_body,
        "worst_comment_link": worst_comment_link,
        "discussed_comment_author": discussed_comment_author,
        "discussed_comment_answers": discussed_comment_answers,
        "discussed_comment_body": discussed_comment_body,
        "discussed_comment_link": discussed_comment_link,
        "amoureux_author1": amoureux_author1,
        "amoureux_author2": amoureux_author2,
        "amoureux_score": amoureux_score,
        "qualite_author": qualite_author,
        "qualite_score": qualite_score,
        "poc_author": poc_author,
        "poc_score": poc_score,
        "tartine_author": tartine_author,
        "tartine_score": tartine_score,
        "capslock_author": capslock_author,
        "capslock_score": capslock_score,
        "indecision_author": indecision_author,
        "indecision_score": indecision_score,
        "jackpot_author": jackpot_author,
        "jackpot_score": jackpot_score,
        "krach_author": krach_author,
        "krach_score": krach_score,
    }

    return template.safe_substitute(env), best_comment_body


def read_template(file: str) -> str:
    with open(file, "r") as f:
        content = f.read()
    return Template(content)


def main():
    args = parse_args()
    if not args.post_subreddit and not args.no_posting:
        raise ValueError("Post Subreddit not set (use the -p argument).")
    if not Path(args.template_file).is_file():
        raise ValueError(f"File {args.template_file} does not exist.")
    if not Path(args.template_file_title).is_file():
        raise ValueError(f"File {args.template_file_title} does not exist.")

    reddit = redditconnect("bot")
    locale.setlocale(locale.LC_TIME, "fr_FR.utf8")
    # to_string() uses this option to truncate its output
    pd.options.display.max_colwidth = None

    report_day = datetime.now().strftime("%Y-%m-%d") if not args.day else args.day
    logger.info(
        f"Creating report for subreddit {args.report_subreddit} and day {report_day}."
    )
    min_timestamp, max_timestamp = get_timestamp_range(report_day)
    logger.debug(f"Extracting data between {min_timestamp} and {max_timestamp}.")

    # Extract post ids with pushshift
    post_ids = get_pushshift_ids(
        "submission", args.report_subreddit, min_timestamp, max_timestamp, args.test
    )
    if len(post_ids) == 0:
        raise ValueError("post_ids is empty.")

    # Extract current data with praw
    posts, comments = get_data(reddit, post_ids)

    # Convert to pandas dataframe
    df_posts = pd.DataFrame(posts)
    df_comments = pd.DataFrame(comments)

    # Stats calculation + template evaluation
    template = read_template(args.template_file)
    formatted_message, title = format_report(reddit, template, df_posts, df_comments)

    filename = f"{report_day}_{args.report_subreddit}_{int(START_TIME)}.txt"
    logger.info(f"Exporting formatted post to Exports/{filename}")
    Path("Exports").mkdir(parents=True, exist_ok=True)
    with open(f"Exports/{filename}", "w") as f:
        f.write(formatted_message)

    template_title = read_template(args.template_file_title)
    post_title = format_title(template_title, title, report_day)
    if not args.no_posting:
        logger.info(
            f"Sending post to {args.post_subreddit}\nTitle: {post_title}\nContent: {formatted_message}"
        )
        reddit.subreddit(args.post_subreddit).submit(
            title=post_title, selftext=formatted_message
        )
    else:
        logger.info(
            f"Posting is disabled\nTitle: {post_title}\nContent: {formatted_message}"
        )

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
        help="Template file containing the title of the post (required)",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-d",
        "--day",
        help="Report day in format YYYY-MM-DD (default: current day)",
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
    parser.set_defaults(no_posting=False)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == "__main__":
    main()
