import logging
import string
import re
import praw
import pandas as pd
from collections import Counter

logger = logging.getLogger(__name__)


def sanitize_comment_body(body: str) -> str:
    result = " ".join([x for x in body.split("\n") if not x.startswith(">")]).strip()
    return result


def sanitize_long_text(text: str) -> str:
    text = text.replace("\n", "")
    max_length = 150
    if len(text) >= max_length:
        return text[0 : max_length - 1].rsplit(" ", 1)[0] + "…"
    return text


def sanitize_username(username: str) -> str:
    if username in ["None", "/u/None"]:
        return "un inconnu"
    else:
        return username


def sanitize_link(link: str) -> str:
    return f"https://reddit.com{link}?context=2"


def get_best_post(df_posts: pd.DataFrame) -> dict[str, str]:
    """Post with the best score."""
    best_post = df_posts.loc[df_posts["score"].idxmax()]
    return {
        "best_post_author": best_post["author"],
        "best_post_score": best_post["score"],
        "best_post_title": best_post["title"],
        "best_post_link": best_post["permalink"],
        "best_post_id": best_post["id"],
    }


def get_commented_post(df_posts: pd.DataFrame) -> dict[str, str]:
    """Most commented post."""
    subset = df_posts[~df_posts.title.str.startswith("Forum Libre")]
    commented_post = subset.loc[subset["num_comments"].idxmax()]
    return {
        "commented_post_author": commented_post["author"],
        "commented_post_comments": commented_post["num_comments"],
        "commented_post_title": commented_post["title"],
        "commented_post_link": commented_post["permalink"],
        "commented_post_id": commented_post["id"],
    }


def get_best_comment(df_comments: pd.DataFrame) -> dict[str, str]:
    """Comment with the best score."""
    best_comment = df_comments.loc[df_comments["score"].idxmax()]
    return {
        "best_comment_author": best_comment["author"],
        "best_comment_score": best_comment["score"],
        "best_comment_body": sanitize_long_text(best_comment["body"]),
        "best_comment_link": best_comment["permalink"],
        "best_comment_id": best_comment["id"],
    }


def get_worst_comment(df_comments: pd.DataFrame) -> dict[str, str]:
    """Comment with the worst score."""
    worst_comment = df_comments.loc[df_comments["score"].idxmin()]
    return {
        "worst_comment_author": worst_comment["author"],
        "worst_comment_score": worst_comment["score"],
        "worst_comment_body": sanitize_long_text(worst_comment["body"]),
        "worst_comment_link": worst_comment["permalink"],
        "worst_comment_id": worst_comment["id"],
    }


def get_discussed_comment(
    reddit: praw.Reddit, df_comments: pd.DataFrame
) -> dict[str, str]:
    """Comment with the most answers."""
    subset = df_comments[df_comments.parent.str.startswith("t1_")][
        "parent"
    ].value_counts()
    discussed_comment_answers = subset[0]
    discussed_parent_id = subset.idxmax().split("_")[-1]
    discussed_comment = df_comments[df_comments["id"] == discussed_parent_id]
    if not discussed_comment.empty:
        return {
            "discussed_comment_author": discussed_comment.author.to_string(index=False),
            "discussed_comment_answers": discussed_comment_answers,
            "discussed_comment_body": sanitize_long_text(
                discussed_comment.body.to_string(index=False)
            ),
            "discussed_comment_link": discussed_comment.permalink.to_string(
                index=False
            ),
            "discussed_comment_id": discussed_comment.id.to_string(index=False),
        }
    else:
        logger.warning(
            "Most discussed comment is not in df_comments. Extracting it separately."
        )
        comment = reddit.comment(discussed_parent_id)
        comment.refresh()
        return {
            "discussed_comment_author": comment.author,
            "discussed_comment_answers": str(len(comment.replies)),
            "discussed_comment_body": sanitize_long_text(comment.body),
            "discussed_comment_link": f"https://reddit.com{comment.permalink}",
            "discussed_comment_id": discussed_parent_id,
        }


def get_amoureux(df_comments: pd.DataFrame) -> dict[str, str]:
    """Two users that interacted with each other the most."""
    # filter comments answering to another comment
    subset = df_comments[df_comments.parent.str.startswith("t1_")]
    subset.loc[:, "parent_id"] = subset.parent.str.split("_").str[-1]
    subset2 = subset.set_index("id").join(subset.set_index("parent_id"), rsuffix="_new")
    subset3 = (
        subset2[subset2.author_new.notnull()][["author", "author_new"]]
        .apply(Counter, axis="columns")
        .value_counts()
    )
    score = subset3[0]
    authors = [x for x, y in subset3.index[0].items()]
    return {
        "amoureux_author1": str(authors[0]),
        "amoureux_author2": str(authors[1]),
        "amoureux_score": score,
    }


def get_qualite(df_comments: pd.DataFrame) -> dict[str, str]:
    """From : https://www.reddit.com/r/BestOfFrance/wiki/index
    Le prix qualité récompense le participant qui a le meilleur rapport "karma par caractère tapés".
    Pour prétendre à ce titre, il faut avoir contribué au moins 140 caractères dans la journée.
    Le score est mesuré en milliSPHKS en l'honneur de /u/sphks qui a suggéré cette fonctionnalité (1 SPHKS = 1 point de karma par caractère)."""
    subset = df_comments.groupby(["author"]).sum()
    subset2 = subset[subset.length > 140].copy()
    subset2.loc[:, "milliSPHKS"] = subset2["score"] / subset2["length"] * 1000
    qualite_author = subset2.loc[subset2["milliSPHKS"].idxmax()]
    return {
        "qualite_author": qualite_author.name,
        "qualite_score": round(qualite_author["milliSPHKS"], 2),
    }


def get_poc(df_comments: pd.DataFrame) -> dict[str, str]:
    """User that posted the most comments."""
    poc = df_comments["author"].value_counts()
    return {
        "poc_author": str(poc.idxmax()),
        "poc_score": poc[0],
    }


def get_tartine(df_comments: pd.DataFrame) -> dict[str, str]:
    """User that typed the most characters."""
    subset = df_comments.groupby(["author"]).sum()["length"]
    return {
        "tartine_author": str(subset.idxmax()),
        "tartine_score": subset[subset.idxmax()],
    }


def get_capslock(df_comments: pd.DataFrame) -> dict[str, str]:
    """User that typed the most uppercase characters."""
    subset = df_comments
    # replace punctuation with space so they don't count as characters in words
    subset["body2"] = subset["body"].str.replace(
        "[{}]".format(string.punctuation), " ", regex=True
    )
    subset["capslock"] = subset["body2"].apply(
        lambda row: sum([len(x) for x in row.split() if x.isupper()])
    )
    subset2 = subset.groupby("author").sum()["capslock"]
    return {
        "capslock_author": str(subset2.idxmax()),
        "capslock_score": subset2[subset2.idxmax()],
    }


def get_indecision(df_comments: pd.DataFrame) -> dict[str, str]:
    """User that typed the most ? characters"""
    subset = df_comments
    # delete all non-question marks characters and remove repeated question marks
    subset["body2"] = (
        subset["body"]
        .str.replace(
            "[{}]".format(string.punctuation.replace("?", "")), ".", regex=True
        )
        .str.replace(r"\?+", "?", regex=True)
        .str.replace(r"\.+", ".", regex=True)
    )
    subset["question"] = subset["body2"].apply(
        lambda row: len(
            [
                x
                for x in row.rsplit("?", 1)[0].split("?")
                if (x and bool(re.search(r"\w", x)))
            ]
        )
        if "?" in row
        else 0
    )
    subset2 = subset.groupby("author").sum()["question"]
    return {
        "indecision_author": str(subset2.idxmax()),
        "indecision_score": subset2[subset2.idxmax()],
    }


def get_jackpot(df_comments: pd.DataFrame) -> dict[str, str]:
    """User that gained the most karma."""
    subset = df_comments.groupby(["author"]).sum()["score"]
    return {
        "jackpot_author": str(subset.idxmax()),
        "jackpot_score": subset[subset.idxmax()],
    }


def get_krach(df_comments: pd.DataFrame) -> dict[str, str]:
    """User that lost the most karma."""
    subset = df_comments.groupby(["author"]).sum()["score"]
    return {
        "krach_author": str(subset.idxmin()),
        "krach_score": subset[subset.idxmin()],
    }
