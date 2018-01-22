## Twitter Democracy


#### Aim

Gauge popularity of people and events by analysing tweets concerning them.

Starting off with Jeremy Corbyn to stay simple.


#### Prerequisites

Create a sqlite3 database by navigating to the repository at the command line and typing `sqlite3 tweets.db < createdb.sql`.

Folder must contain a `credentials.py` file defining tokens for Twitter's OAuth.

#### Files

`corbyn_tweets.py` retrieves tweets for a specified amount of time and stores them in `tweets.db`.

`corbyn_tweets_plot.py` completes the data pipeline by loading tweets from `tweets.db`, then uses `dynamic_plot()` to draw real time dynamic plots or `instant_plot()` to save a plot created from the current database as if it were static.
