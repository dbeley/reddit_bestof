"""Create and send Reddit BestOf reports."""
import logging
import time
import argparse
import praw
import locale
from datetime import datetime
from pathlib import Path

logger = logging.getLogger()
logging.getLogger("praw").setLevel(logging.WARNING)
START_TIME = time.time()
VALID_PUSHSHIFT_TYPES = ["submission", "comment"]


def redditconnect(config_section: str):
    user_agent = "python:script:reddit_bestof"
    reddit = praw.Reddit(config_section, user_agent=user_agent)
    return reddit


def read_file(file: str) -> str:
    if not Path(file).is_file():
        raise ValueError(f"File {file} does not exist.")
    with open(file, "r") as f:
        content = f.read()
    return content


def format_title(formatted_message: str, filename: str) -> str:
    """Function only useful for /r/BestOfFrance2."""
    day = Path(filename).stem.split("_")[0]
    y, m, d = [int(x) for x in day.split("-", 3)]
    date = datetime(y, m, d).strftime("%A %d %b %Y")
    best_comment = formatted_message.split("##")[3].split("[")[1].split("]")[0]
    formatted_title = f"[BestOf] du {date} : {best_comment}"
    return formatted_title


def main():
    args = parse_args()
    reddit = redditconnect("bot")
    locale.setlocale(locale.LC_TIME, "fr_FR.utf8")

    formatted_message = read_file(args.file)
    post_title = format_title(formatted_message, args.file)

    if not args.no_posting:
        logger.info(
            f"Sending post to {args.post_subreddit}.\nTitle: {post_title}.\nContent: {formatted_message}"
        )
        reddit.subreddit(args.post_subreddit).submit(
            title=post_title, selftext=formatted_message
        )
    else:
        logger.info(
            f"Sending to reddit is disabled.\nTitle: {post_title}.\nContent: {formatted_message}"
        )

    logger.info("Runtime: %.2f seconds." % (time.time() - START_TIME))


def parse_args():
    parser = argparse.ArgumentParser(description="Send a BestOf report to reddit.")
    parser.add_argument(
        "--debug",
        help="Display debugging information",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    parser.add_argument(
        "-p",
        "--post_subreddit",
        help="Subreddit to send the formatted message to (required, without prefix, example: bestoffrance2)",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-f",
        "--file",
        help="File containing the content of the post",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--no_posting",
        help="Disable posting to reddit",
        dest="no_posting",
        action="store_true",
    )
    parser.set_defaults(no_posting=False)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == "__main__":
    main()
