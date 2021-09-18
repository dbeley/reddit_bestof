# reddit_bestof

Work-in-progress.

`reddit_bestof` is a python tool used to generate the reports at [**/r/BestOfFrance2**](https://reddit.com/r/bestoffrance2).

It is intended to be run every day at 9 pm. It will:
	- extract the activity of a subreddit for the last day (from yesterday 9 pm to today 9 pm)
	- create a report from a template
	- export the report to a text file
	- (optional) send it to a new post in a subreddit of your choice

It is designed to be as generic as possible so it should work with any subreddit.

## Configuration

Rename `praw_sample.ini` to `praw.ini` and put your informations in it. You can create an API dev script at https://old.reddit.com/prefs/apps/.

## Installation

Classic installation:
```
git clone https://github.com/dbeley/reddit_bestof
cd reddit_bestof
python setup.py
```

Installation in a virtualenv (with pipenv):
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
                     [--no_posting] [--test]

Create and send Reddit BestOf reports.

optional arguments:
  -h, --help            show this help message and exit
  --debug               Display debugging information
  -s REPORT_SUBREDDIT, --report_subreddit REPORT_SUBREDDIT
                        Subreddit (required, without prefix, example: france)
  -f TEMPLATE_FILE, --template_file TEMPLATE_FILE
                        Template file containing the content of the post
                        (required)
  -t TEMPLATE_FILE_TITLE, --template_file_title TEMPLATE_FILE_TITLE
                        Template file containing the title of the post
                        (required)
  -d DAY, --day DAY     Report day in format YYYY-MM-DD (default: current day)
  -p POST_SUBREDDIT, --post_subreddit POST_SUBREDDIT
                        Subreddit to send the formatted message to (without
                        prefix, example: bestoffrance2)
  --no_posting          Disable posting to Reddit
  --test                Use a very small subset of data
```

### Example

Create a report for /r/france for 2021-09-16 using template_besoffrance.txt as post template and template_bestoffrance_title as title template and post it to /r/bestoffrance2:
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

## Scripts

- `manually_send_report.py`: manually send a report created with `reddit_bestof`

```
python manually_send_report.py -h
```

```
usage: manually_send_report.py [-h] [--debug] -p POST_SUBREDDIT -f FILE
                               [--no_posting]

Send a BestOf report to reddit.

optional arguments:
  -h, --help            show this help message and exit
  --debug               Display debugging information
  -p POST_SUBREDDIT, --post_subreddit POST_SUBREDDIT
                        Subreddit to send the formatted message to (required,
                        without prefix, example: bestoffrance2)
  -f FILE, --file FILE  File containing the content of the post
  --no_posting          Disable posting to reddit
```

## TODO

- add records for each category
- add gilded comments
