import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def test_posts_dataframe():
    data = pd.DataFrame(
        np.array(
            [
                ["author1", 12, 10, "title1", "permalink1", "id1"],
                ["author2", 20, -1, "title2", "permalink2", "id2"],
                ["author3", 0, 10, "title3", "permalink3", "id3"],
                ["author4", 20, 5, "title4", "permalink4", "id4"],
                ["author4", 40, 5, "Forum Libre 123", "permalink4", "id4"],
            ]
        ),
        columns=["author", "num_comments", "score", "title", "permalink", "id"],
    )
    data["num_comments"] = pd.to_numeric(data["num_comments"])
    data["score"] = pd.to_numeric(data["score"])
    yield data


@pytest.fixture
def test_simple_comments_dataframe():
    data = pd.DataFrame(
        np.array(
            [
                ["author1", 3, "body1", "permalink1", "id1"],
                ["author2", 3, "body2", "permalink2", "id2"],
                ["author3", 2, "body3", "permalink3", "id3"],
                ["author4", -1, "body4", "permalink4", "id4"],
                ["author5", 1, "body5", "permalink5", "id5"],
            ]
        ),
        columns=["author", "score", "body", "permalink", "id"],
    )
    data["score"] = pd.to_numeric(data["score"])
    yield data


@pytest.fixture
def test_score_comments_dataframe():
    data = pd.DataFrame(
        np.array(
            [
                ["author1", 30, "body1", "permalink1", "id1"],
                ["author1", 90, "body1", "permalink1", "id2"],
                ["author1", 3, "body1", "permalink1", "id3"],
                ["author2", -10, "body2", "permalink2", "id4"],
                ["author2", 0, "body2", "permalink2", "id5"],
                ["author3", 2, "body3", "permalink3", "id6"],
                ["author4", -10, "body4", "permalink4", "id7"],
                ["author5", 1000, "body5", "permalink5", "id8"],
                ["author5", -931, "body5", "permalink5", "id9"],
            ]
        ),
        columns=["author", "score", "body", "permalink", "id"],
    )
    data["score"] = pd.to_numeric(data["score"])
    yield data


@pytest.fixture
def test_amoureux_comments_dataframe():
    data = pd.DataFrame(
        np.array(
            [
                ["author1", 1, "body1", "permalink1", "id1", "t1_id4"],
                ["author1", 1, "body2", "permalink2", "id2", "t1_id4"],
                ["author1", 1, "body3", "permalink3", "id3", "t1_id4"],
                ["author2", 1, "body4", "permalink4", "id4", "t1_id1"],
                ["author1", 1, "body5", "permalink5", "id5", "t1_id6"],
                ["author3", 1, "body6", "permalink6", "id6", "t1_id4"],
                ["author3", 1, "body7", "permalink7", "id7", "t1_id4"],
                ["author2", 1, "body8", "permalink8", "id8", "t1_id7"],
            ]
        ),
        columns=["author", "score", "body", "permalink", "id", "parent"],
    )
    data["score"] = pd.to_numeric(data["score"])
    yield data


@pytest.fixture
def test_qualite_comments_dataframe():
    data = pd.DataFrame(
        np.array(
            [
                ["author1", 1, "abcdefghijklmnopqrstuvwxyz", "permalink1", "id1"],
                ["author1", 3, "abcdefghijklmnopqrstuvwxyz", "permalink2", "id2"],
                ["author1", 8, "abcdefghijklmnopqrstuvwxyz", "permalink3", "id3"],
                ["author1", 1, "abcdefghijklmnopqrstuvwxyz", "permalink1", "id1"],
                ["author1", 9, "abcdefghijklmnopqrstuvwxyz", "permalink2", "id2"],
                ["author1", 2, "abcdefghijklmnopqrstuvwxyz", "permalink3", "id3"],
                ["author2", 1, "abcdefghijklmnopqrstuvwxyz", "permalink4", "id4"],
                ["author2", 1, "abcdefghijklmnopqrstuvwxyz", "permalink5", "id5"],
                ["author2", 1, "abcdefghijklmnopqrstuvwxyz", "permalink6", "id6"],
                ["author3", 1, "abcdefghijklmnopqrstuvwxyz", "permalink7", "id7"],
                ["author3", 1, "abcdefghijklmnopqrstuvwxyz", "permalink8", "id8"],
                ["author3", 1, "abcdefghijklmnopqrstuvwxyz", "permalink8", "id8"],
                ["author3", 1, "abcdefghijklmnopqrstuvwxyz", "permalink8", "id8"],
                ["author3", 1, "abcdefghijklmnopqrstuvwxyz", "permalink8", "id8"],
                ["author3", 1, "abcdefghijklmnopqrstuvwxyz", "permalink8", "id8"],
            ]
        ),
        columns=["author", "score", "body", "permalink", "id"],
    )
    data["score"] = pd.to_numeric(data["score"])
    data["length"] = data["body"].str.len()
    yield data


@pytest.fixture
def test_poc_comments_dataframe():
    data = pd.DataFrame(
        np.array(
            [
                ["author1", 1, "body1", "permalink1", "id1", "t1_id4"],
                ["author1", 1, "body2", "permalink2", "id2", "t1_id4"],
                ["author1", 1, "body3", "permalink3", "id3", "t1_id4"],
                ["author2", 1, "body4", "permalink4", "id4", "t1_id1"],
                ["author1", 1, "body5", "permalink5", "id5", "t1_id6"],
                ["author3", 1, "body6", "permalink6", "id6", "t1_id4"],
                ["author3", 1, "body7", "permalink7", "id7", "t1_id4"],
                ["author2", 1, "body8", "permalink8", "id8", "t1_id7"],
            ]
        ),
        columns=["author", "score", "body", "permalink", "id", "parent"],
    )
    data["score"] = pd.to_numeric(data["score"])
    yield data


@pytest.fixture
def test_tartine_comments_dataframe():
    data = pd.DataFrame(
        np.array(
            [
                ["author1", 1, "abcdefghijklmnopqrstuvwxyz", "permalink1", "id1"],
                ["author1", 3, "abcdefghijklmnopqrstuvwxyz", "permalink2", "id2"],
                ["author1", 8, "abcdefghijklmnopqrstuvwxyz", "permalink3", "id3"],
                ["author1", 1, "abcdefghijklmnopqrstuvwxyz", "permalink1", "id1"],
                ["author1", 9, "abcdefghijklmnopqrstuvwxyz", "permalink2", "id2"],
                ["author1", 2, "abcdefghijklmnopqrstuvwxyz", "permalink3", "id3"],
                ["author2", 1, "abcdefghijklmnopqrstuvwxyz", "permalink4", "id4"],
                ["author2", 1, "abcdefghijklmnopqrstuvwxyz", "permalink5", "id5"],
                ["author2", 1, "abcdefghijklmnopqrstuvwxyz", "permalink6", "id6"],
                ["author3", 1, "abcdefghijklmnopqrstuvwxyz", "permalink7", "id7"],
                ["author3", 1, "abcdefghijklmnopqrstuvwxyz", "permalink8", "id8"],
                ["author3", 1, "abcdefghijklmnopqrstuvwxyz", "permalink8", "id8"],
                ["author3", 1, "abcdefghijklmnopqrstuvwxyz", "permalink8", "id8"],
                ["author3", 1, "abcdefghijklmnopqrstuvwxyz", "permalink8", "id8"],
                ["author3", 1, "abcdefghijklmnopqrstuvwxyz", "permalink8", "id8"],
            ]
        ),
        columns=["author", "score", "body", "permalink", "id"],
    )
    data["score"] = pd.to_numeric(data["score"])
    data["length"] = data["body"].str.len()
    yield data


@pytest.fixture
def test_capslock_comments_dataframe():
    data = pd.DataFrame(
        np.array(
            [
                [
                    "author1",
                    1,
                    "Une phrase",
                    "permalink1",
                    "id1",
                ],
                ["author1", 3, "CECI COMPTE!!#$@!", "permalink2", "id2"],
                [
                    "author1",
                    7,
                    "Ça ne compte pas. ÇA COMPTE. Ça Non !!!",
                    "permalink2",
                    "id3",
                ],
                ["author1", 2, "JE VOUS DEMANDE DE VOUS ARRÊTER.", "permalink2", "id4"],
                ["author2", 3, "abcdefghijklmnopqrstuvwxyz", "permalink2", "id5"],
                ["author2", 3, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "permalink2", "id6"],
            ]
        ),
        columns=["author", "score", "body", "permalink", "id"],
    )
    data["score"] = pd.to_numeric(data["score"])
    data["length"] = data["body"].str.len()
    yield data


@pytest.fixture
def test_indecision_comments_dataframe():
    data = pd.DataFrame(
        np.array(
            [
                [
                    "author1",
                    3,
                    "On en parle ??? C'est une question ?",
                    "permalink1",
                    "id1",
                ],
                ["author1", 3, "Quoi ?!!?!! Autre question!!!!!?", "permalink2", "id2"],
                [
                    "author1",
                    3,
                    "Vraiment?!?!?Bizarre??!?! Pas de question ici. Trois questions ??!!Normalement.",
                    "permalink3",
                    "id3",
                ],
                ["author1", 3, "?????????????????????????", "permalink4", "id4"],
                ["author2", 3, "?????????????????????????", "permalink5", "id5"],
            ]
        ),
        columns=["author", "score", "body", "permalink", "id"],
    )
    data["score"] = pd.to_numeric(data["score"])
    data["length"] = data["body"].str.len()
    yield data
