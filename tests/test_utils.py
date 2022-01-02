from reddit_bestof import utils


def test_sanitize_comment_body():
    comment_body = "> comment1\nline of text1\n> comment2\nline of text2"

    comment_body_expected = "line of text1 line of text2"
    assert utils.sanitize_comment_body(comment_body) == comment_body_expected


def test_sanitize_long_text():
    small_text = "abcdefg"
    long_text = "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz"
    long_text_expected = "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrs…"
    assert utils.sanitize_long_text(small_text) == small_text
    assert utils.sanitize_long_text(long_text) == long_text_expected

    small_text2 = "1234"
    small_text2_expected = "123…"
    assert utils.sanitize_long_text(small_text2, 4) == small_text2_expected


def test_sanitize_username():
    unknown_username = "None"
    unknown_username_expected = "un inconnu"

    assert utils.sanitize_username(unknown_username) == unknown_username_expected


def test_sanitize_link():
    link = "/test"
    link_expected = "https://reddit.com/test?context=2"

    assert utils.sanitize_link(link) == link_expected


def test_get_best_post(test_posts_dataframe):
    expected_result = {
        "best_post_author": "author1",
        "best_post_score": 10,
        "best_post_title": "title1",
        "best_post_link": "permalink1",
        "best_post_id": "id1",
    }
    print(utils.get_best_post(test_posts_dataframe))

    assert utils.get_best_post(test_posts_dataframe) == expected_result


def test_get_commented_post(test_posts_dataframe):
    expected_result = {
        "commented_post_author": "author2",
        "commented_post_comments": 20,
        "commented_post_title": "title2",
        "commented_post_link": "permalink2",
        "commented_post_id": "id2",
    }
    print(utils.get_commented_post(test_posts_dataframe))

    assert utils.get_commented_post(test_posts_dataframe) == expected_result


def test_get_best_comment(test_simple_comments_dataframe):
    expected_result = {
        "best_comment_author": "author1",
        "best_comment_score": 3,
        "best_comment_body": "body1",
        "best_comment_link": "permalink1",
        "best_comment_id": "id1",
    }
    print(utils.get_best_comment(test_simple_comments_dataframe))

    assert utils.get_best_comment(test_simple_comments_dataframe) == expected_result


def test_get_worst_comment(test_simple_comments_dataframe):
    expected_result = {
        "worst_comment_author": "author4",
        "worst_comment_score": -1,
        "worst_comment_body": "body4",
        "worst_comment_link": "permalink4",
        "worst_comment_id": "id4",
    }
    print(utils.get_worst_comment(test_simple_comments_dataframe))

    assert utils.get_worst_comment(test_simple_comments_dataframe) == expected_result


# def test_get_discussed_comment(test_simple_comments_dataframe):
#     expected_result = {
#         "discussed_comment_author": "author4",
#         "discussed_comment_score": -1,
#         "discussed_comment_body": "body4",
#         "discussed_comment_link": "permalink4",
#         "discussed_comment_id": "id4",
#     }
#     print(utils.get_discussed_comment(reddit, test_simple_comments_dataframe))

#     assert (
#         utils.get_discussed_comment(reddit, test_simple_comments_dataframe) == expected_result
#     )


def test_get_amoureux(test_amoureux_comments_dataframe):
    expected_result = {
        "amoureux_author1": "author1",
        "amoureux_author2": "author2",
        "amoureux_score": 4,
    }
    print(utils.get_amoureux(test_amoureux_comments_dataframe))

    assert utils.get_amoureux(test_amoureux_comments_dataframe) == expected_result


def test_get_qualite(test_qualite_comments_dataframe):
    expected_result = {"qualite_author": "author1", "qualite_score": 153.85}

    print(test_qualite_comments_dataframe)
    print(utils.get_qualite(test_qualite_comments_dataframe))

    assert utils.get_qualite(test_qualite_comments_dataframe) == expected_result


def test_get_poc(test_poc_comments_dataframe):
    expected_result = {"poc_author": "author1", "poc_score": 4}

    print(test_poc_comments_dataframe)
    print(utils.get_poc(test_poc_comments_dataframe))

    assert utils.get_poc(test_poc_comments_dataframe) == expected_result


def test_get_tartine(test_tartine_comments_dataframe):
    expected_result = {"tartine_author": "author1", "tartine_score": 156}

    print(test_tartine_comments_dataframe)
    print(utils.get_tartine(test_tartine_comments_dataframe))

    assert utils.get_tartine(test_tartine_comments_dataframe) == expected_result


def test_get_capslock(test_capslock_comments_dataframe):
    expected_result = {"capslock_author": "author1", "capslock_score": 44}

    print(test_capslock_comments_dataframe)
    print(utils.get_capslock(test_capslock_comments_dataframe))

    assert utils.get_capslock(test_capslock_comments_dataframe) == expected_result


def test_get_indecision(test_indecision_comments_dataframe):
    expected_result = {"indecision_author": "author1", "indecision_score": 7}

    print(test_indecision_comments_dataframe)
    print(utils.get_indecision(test_indecision_comments_dataframe))

    assert utils.get_indecision(test_indecision_comments_dataframe) == expected_result


def test_get_jackpot(test_score_comments_dataframe):
    expected_result = {"jackpot_author": "author1", "jackpot_score": 123}

    print(test_score_comments_dataframe)
    print(utils.get_jackpot(test_score_comments_dataframe))

    assert utils.get_jackpot(test_score_comments_dataframe) == expected_result


def test_get_krach(test_score_comments_dataframe):
    expected_result = {"krach_author": "author2", "krach_score": -10}

    print(test_score_comments_dataframe)
    print(utils.get_krach(test_score_comments_dataframe))

    assert utils.get_krach(test_score_comments_dataframe) == expected_result
