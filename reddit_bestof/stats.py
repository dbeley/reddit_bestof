import logging
from collections import Counter

logger = logging.getLogger(__name__)


def sanitize_long_text(text: str) -> str:
    text = text.replace("\n", "")
    max_length = 150
    return text[0 : max_length - 1] + "…" if len(text) > max_length else text


def get_best_post(df_posts):
    best_post = df_posts.loc[df_posts["score"].idxmax()]
    return (
        "/u/" + best_post["author"],
        best_post["score"],
        best_post["title"],
        best_post["permalink"],
    )


def get_best_comment(df_comments):
    best_comment = df_comments.loc[df_comments["score"].idxmax()]
    return (
        "/u/" + best_comment["author"],
        best_comment["score"],
        sanitize_long_text(best_comment["body"]),
        best_comment["permalink"],
    )


def get_worst_comment(df_comments):
    worst_comment = df_comments.loc[df_comments["score"].idxmin()]
    return (
        "/u/" + worst_comment["author"],
        worst_comment["score"],
        sanitize_long_text(worst_comment["body"]),
        worst_comment["permalink"],
    )


def get_discussed_comment(reddit, df_comments):
    subset = df_comments[df_comments.parent.str.startswith("t1_")][
        "parent"
    ].value_counts()
    discussed_comment_answers = subset[0]
    discussed_parent_id = subset.idxmax().split("_")[-1]
    discussed_comment = df_comments[df_comments["id"] == discussed_parent_id]
    if not discussed_comment.empty:
        return (
            "/u/" + discussed_comment["author"],
            discussed_comment_answers,
            sanitize_long_text(discussed_comment["body"]),
            discussed_comment["permalink"],
        )
    else:
        logger.warning(
            "Most discussed comment is not in df_comments. Extracting it separately."
        )
        comment = reddit.comment(discussed_parent_id)
        comment.refresh()
        return (
            "/u/" + str(comment.author),
            len(comment.replies),
            sanitize_long_text(comment.body),
            f"https://reddit.com{comment.permalink}",
        )


def get_amoureux(df_comments):
    # filter comments answering to another comment
    subset = df_comments[df_comments.parent.str.startswith("t1_")]
    subset["parent_id"] = subset["parent"].str.split("_").str[-1]
    subset2 = subset.set_index("id").join(subset.set_index("parent_id"), rsuffix="_new")
    subset3 = (
        subset2[subset2.author_new.notnull()][["author", "author_new"]]
        .apply(Counter, axis="columns")
        .value_counts()
    )
    score = subset3[0]
    authors = [x for x, y in subset3.index[0].items()]
    breakpoint()
    return "/u/" + authors[0], "/u/" + authors[1], score


def get_qualite(df_comments):
    """From : https://www.reddit.com/r/BestOfFrance/wiki/index
    Le prix qualité récompense le participant qui a le meilleur rapport "karma par caractère tapés".
    Pour prétendre à ce titre, il faut avoir contribué au moins 140 caractères dans la journée.
    Le score est mesuré en milliSPHKS en l'honneur de /u/sphks qui a suggéré cette fonctionnalité (1 SPHKS = 1 point de karma par caractère)."""
    subset = df_comments.groupby(["author"]).sum()
    subset2 = subset[subset.length > 140]
    subset2["milliSPHKS"] = subset2["score"] / subset2["length"] * 1000
    qualite_author = subset2.loc[subset2["milliSPHKS"].idxmax()]
    return "/u/" + str(qualite_author.name), round(qualite_author["milliSPHKS"], 2)


def get_poc(df_comments):
    poc = df_comments["author"].value_counts()
    return "/u/" + poc.idxmax(), poc[0]


def get_tartine(df_comments):
    subset = df_comments.groupby(["author"]).sum()["length"]
    return "/u/" + subset.idxmax(), subset[subset.idxmax()]


def get_capslock(df_comments):
    subset = df_comments
    subset["capslock"] = subset["body"].str.count(r"[A-Z]")
    subset2 = subset.groupby("author").sum()["capslock"]
    return "/u/" + subset2.idxmax(), subset2[subset2.idxmax()]


def get_indecision(df_comments):
    subset = df_comments
    subset["question"] = subset["body"].str.count(r"[?]")
    subset2 = subset.groupby("author").sum()["question"]
    return "/u/" + subset2.idxmax(), subset2[subset2.idxmax()]


def get_jackpot(df_comments):
    subset = df_comments.groupby(["author"]).sum()["score"]
    return "/u/" + subset.idxmax(), subset[subset.idxmax()]


def get_krach(df_comments):
    subset = df_comments.groupby(["author"]).sum()["score"]
    return "/u/" + subset.idxmin(), subset[subset.idxmin()]
