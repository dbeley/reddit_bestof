# reddit_bestof

Work-in-progress.

`reddit_bestof` is a python tool used to generate the reports at **/r/BestOfFrance2**.

It is intended to be run every day at 9 pm. It will extract the activity of the subreddit for the last day and create a report from it.

It is designed to be as generic as possible.

## Configuration

Rename `praw_sample.ini` to `praw.ini` and put your informations in it. You can create an API dev script at https://old.reddit.com/prefs/apps/.

## Installation

Classic installation
```
git clone https://github.com/dbeley/reddit_bestof
cd reddit_bestof
python setup.py
```

Installation in a virtualenv (with pipenv)
```
git clone https://github.com/dbeley/reddit_bestof
cd reddit_bestof
pipenv install '-e .'
```

## Usage

```
reddit_bestof -h
```

```
usage: reddit_bestof [-h] [--debug] -s REPORT_SUBREDDIT -f TEMPLATE_FILE -t
                     TEMPLATE_FILE_TITLE [-d DAY] [-p POST_SUBREDDIT]
                     [--no_posting]

Create and send Reddit BestOf reports.

optional arguments:
  -h, --help            show this help message and exit
  --debug               Display debugging information
  -s REPORT_SUBREDDIT, --report_subreddit REPORT_SUBREDDIT
                        Subreddit (required, without prefix, example: france).
  -f TEMPLATE_FILE, --template_file TEMPLATE_FILE
                        Template file containing the content of the post
                        (required).
  -t TEMPLATE_FILE_TITLE, --template_file_title TEMPLATE_FILE_TITLE
                        Template file containing the title of the post
                        (required).
  -d DAY, --day DAY     Report day in format YYYY-MM-DD (default: current
                        day).
  -p POST_SUBREDDIT, --post_subreddit POST_SUBREDDIT
                        Subreddit to send the formatted message to (without
                        prefix, example: bestoffrance2).
  --no_posting          Disable posting to Reddit.
```

### Example

```
reddit_bestof -s france -d "2021-09-16" -p bestoffrance2 -f template_bestoffrance.txt -t template_bestoffrance_title.txt
```

### Templates

The script uses two templates: one for the post content, the other for the post title.

See `template_bestoffrance.txt` and `template_bestoffrance_title.txt` for examples.

## Systemd-service

You can schedule the script to run every day at a certain time (by default 21:00). You will need to modify `reddit_bestof.service` to reflect your configuration.

```
cp systemd-service/* ~/.config/systemd/user
systemctl --user daemon-reload
systemctl --user enable --now reddit_bestof.timer
systemctl --user start reddit_bestof
```

## TODO

- filter out deleted/hidden posts/comments
- add records for each category
- add gilded comments
- convert to script to use a stream?
