# reddit_bestof

`reddit_bestof` is a python tool used to generate reddit best-of reports.

You can see it in action here:

- [**/r/BestOfFrance**](https://reddit.com/r/bestoffrance)
- [**/r/BestOfFrance2**](https://reddit.com/r/bestoffrance2) (inactive)

It is intended to be run every day at 9 pm. It will:

- extract the activity of a subreddit for the last day (from yesterday 9 pm to today 9 pm)
- create a report from a template
- export the report to a text file
- (optional) send it to a new post in a subreddit of your choice
- (optional) notify the users mentioned in the report

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
usage: reddit_bestof [-h] [--debug] -s SUBREDDIT -f TEMPLATE_FILE -t
                     TEMPLATE_FILE_TITLE [-m TEMPLATE_FILE_MESSAGE] [-d DAY]
                     [-p POST_SUBREDDIT] [--no_posting] [--test]
                     [--notify_winners]

Create and send Reddit BestOf reports.

optional arguments:
  -h, --help            show this help message and exit
  --debug               Display debugging information
  -s SUBREDDIT, --subreddit SUBREDDIT
                        Subreddit (required, without prefix, example: france)
  -f TEMPLATE_FILE, --template_file TEMPLATE_FILE
                        Template file containing the content of the post
                        (required)
  -t TEMPLATE_FILE_TITLE, --template_file_title TEMPLATE_FILE_TITLE
                        Template file containing the title of the post
                        (required)
  -m TEMPLATE_FILE_MESSAGE, --template_file_message TEMPLATE_FILE_MESSAGE
                        Template file containing the message for the winner's
                        notification (required if --notify-winners is set)
  -d DAY, --day DAY     Report day in format YYYY-MM-DD (optional, if not set:
                        current day)
  -p POST_SUBREDDIT, --post_subreddit POST_SUBREDDIT
                        Subreddit to send the formatted message to (without
                        prefix, example: bestoffrance2)
  --no_posting          Disable posting to Reddit
  --test                Use a very small subset of data
  --notify_winners      Send a message to winners
```

### Example

Create a report for `/r/france` for the current day using `template_post.txt` as post template, `template_title.txt` as title template, `template_message.txt` as message template and post it to `/r/bestoffrance2`:
```
reddit_bestof -s france -p bestoffrance2 -f template_post.txt -t template_title.txt -m template_message.txt
```

### Templates

The script uses three templates:

- post content
- post title
- winner message

See the `templates` folder for examples.

## Systemd-service

You can schedule the script to run every day at a specific time (by default 21:00). You will need to modify `reddit_bestof.service` to reflect your configuration.

```
cp systemd-service/* ~/.config/systemd/user
systemctl --user daemon-reload
systemctl --user enable --now reddit_bestof.timer # enable the timer
systemctl --user start reddit_bestof # you can also run the service manually
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
- improve datetime handling
- notify all mentioned users
