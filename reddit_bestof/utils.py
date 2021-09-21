import logging
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


def get_best_post(df_posts: pd.DataFrame) -> (str, str, str, str):
    best_post = df_posts.loc[df_posts["score"].idxmax()]
    return {
        "best_post_author": sanitize_username("/u/" + str(best_post["author"])),
        "best_post_score": best_post["score"],
        "best_post_title": best_post["title"],
        "best_post_link": best_post["permalink"],
    }


def get_best_comment(df_comments: pd.DataFrame) -> (str, str, str, str):
    best_comment = df_comments.loc[df_comments["score"].idxmax()]
    return {
        "best_comment_author": sanitize_username("/u/" + str(best_comment["author"])),
        "best_comment_score": best_comment["score"],
        "best_comment_body": sanitize_long_text(best_comment["body"]),
        "best_comment_link": best_comment["permalink"],
    }


def get_worst_comment(df_comments: pd.DataFrame) -> (str, str, str, str):
    worst_comment = df_comments.loc[df_comments["score"].idxmin()]
    return {
        "wors_comment_author": sanitize_username("/u/" + str(worst_comment["author"])),
        "wors_comment_score": worst_comment["score"],
        "wors_comment_body": sanitize_long_text(worst_comment["body"]),
        "wors_comment_link": worst_comment["permalink"],
    }


def get_discussed_comment(
    reddit: praw.Reddit, df_comments: pd.DataFrame
) -> (str, str, str, str):
    subset = df_comments[df_comments.parent.str.startswith("t1_")][
        "parent"
    ].value_counts()
    discussed_comment_answers = subset[0]
    discussed_parent_id = subset.idxmax().split("_")[-1]
    discussed_comment = df_comments[df_comments["id"] == discussed_parent_id]
    if not discussed_comment.empty:
        return {
            "discussed_comment_author": sanitize_username(
                "/u/" + str(discussed_comment.author.to_string(index=False))
            ),
            "discussed_comment_answers": discussed_comment_answers,
            "discussed_comment_body": sanitize_long_text(
                discussed_comment.body.to_string(index=False)
            ),
            "discussed_comment_link": discussed_comment.permalink.to_string(
                index=False
            ),
        }
    else:
        logger.warning(
            "Most discussed comment is not in df_comments. Extracting it separately."
        )
        comment = reddit.comment(discussed_parent_id)
        comment.refresh()
        return {
            "discussed_comment_author": sanitize_username("/u/" + str(comment.author)),
            "discussed_comment_answers": len(comment.replies),
            "discussed_comment_body": sanitize_long_text(comment.body),
            "discussed_comment_link": f"https://reddit.com{comment.permalink}",
        }


def get_amoureux(df_comments: pd.DataFrame) -> (str, str, str):
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
        "amoureux_author1": sanitize_username("/u/" + str(authors[0])),
        "amoureux_author2": sanitize_username("/u/" + str(authors[1])),
        "amoureux_score": score,
    }


def get_qualite(df_comments: pd.DataFrame) -> (str, str):
    """From : https://www.reddit.com/r/BestOfFrance/wiki/index
    Le prix qualité récompense le participant qui a le meilleur rapport "karma par caractère tapés".
    Pour prétendre à ce titre, il faut avoir contribué au moins 140 caractères dans la journée.
    Le score est mesuré en milliSPHKS en l'honneur de /u/sphks qui a suggéré cette fonctionnalité (1 SPHKS = 1 point de karma par caractère)."""
    subset = df_comments.groupby(["author"]).sum()
    subset2 = subset[subset.length > 140]
    subset2.loc[:, "milliSPHKS"] = subset2["score"] / subset2["length"] * 1000
    qualite_author = subset2.loc[subset2["milliSPHKS"].idxmax()]
    return {
        "qualite_author": sanitize_username("/u/" + str(qualite_author.name)),
        "qualite_score": round(qualite_author["milliSPHKS"], 2),
    }


def get_poc(df_comments: pd.DataFrame) -> (str, str):
    poc = df_comments["author"].value_counts()
    return {
        "poc_author": sanitize_username("/u/" + str(poc.idxmax())),
        "poc_score": poc[0],
    }


def get_tartine(df_comments: pd.DataFrame) -> (str, str):
    subset = df_comments.groupby(["author"]).sum()["length"]
    return {
        "tartine_author": sanitize_username("/u/" + str(subset.idxmax())),
        "tartine_score": subset[subset.idxmax()],
    }


def get_capslock(df_comments: pd.DataFrame) -> (str, str):
    subset = df_comments
    subset["capslock"] = subset["body"].str.count(r"[A-Z]")
    subset2 = subset.groupby("author").sum()["capslock"]
    return {
        "capslock_author": sanitize_username("/u/" + str(subset2.idxmax())),
        "capslock_score": subset2[subset2.idxmax()],
    }


def get_indecision(df_comments: pd.DataFrame) -> (str, str):
    subset = df_comments
    subset["question"] = subset["body"].str.count(r"[?]")
    subset2 = subset.groupby("author").sum()["question"]
    return {
        "indecision_author": sanitize_username("/u/" + str(subset2.idxmax())),
        "indecision_score": subset2[subset2.idxmax()],
    }


def get_jackpot(df_comments: pd.DataFrame) -> (str, str):
    subset = df_comments.groupby(["author"]).sum()["score"]
    return {
        "jackpot_author": sanitize_username("/u/" + str(subset.idxmax())),
        "jackpot_score": subset[subset.idxmax()],
    }


def get_krach(df_comments: pd.DataFrame) -> (str, str):
    subset = df_comments.groupby(["author"]).sum()["score"]
    return {
        "krach_author": sanitize_username("/u/" + str(subset.idxmin())),
        "krach_score": subset[subset.idxmin()],
    }
