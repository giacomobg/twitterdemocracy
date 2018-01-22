## Twitter Democracy


#### Aim

Gauge popularity of people and events by analysing tweets concerning them.


#### Prerequisites

Python3, SQLite3

Folder must contain a `credentials.py` file defining tokens for Twitter's OAuth.


#### Files

`corbyn_tweets.py` creates a stream of tweets, filtering with a `search_term`, and stores them in `search_term.db`.

`corbyn_tweets_plot.py` loads tweets from `search_term.db`, then creates graphs with `dynamic_plot()` and `instant_plot()`.