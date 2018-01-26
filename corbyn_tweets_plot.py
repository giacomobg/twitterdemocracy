import sqlite3
import datetime
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import seaborn as sns

class PlotTweets():
    """ Accesses a sqlite3 database containing tweet data and plots it."""
    def __init__(self,time_interval,frames,topics):
        super(PlotTweets, self).__init__()
        self.time_interval = time_interval
        self.frames = frames
        self.topics = topics
        attributes = {
            'axes.facecolor' : '#f0e6f2'
        }
        sns.set(context='paper',style='darkgrid',rc=attributes)
        self.fig, self.ax = plt.subplots()

    def connect_to_db(self,topic):
        """ Connect to sqlite3 db with tweet data."""
        self.db = sqlite3.connect(topic+'.db')

    def get_time_text_data(self):
        """ Retrieve tweet data from sqlite3 db. """
        cursor = self.db.cursor()
        # Retrieving text is currently unnecessary but will be used later
        cursor.execute('''SELECT tweet_time,tweet_text FROM tweets''')
        self.data = cursor.fetchall()

    def data_to_time_intervals(self,addition_var):
        """ Creates two ouputs, xdates and y_values, ready for plotting.
        addition_var takes the text of the tweet
        y_values created by using addition_var to get a number from each tweet and add it on to
        the y value for the right time interval.
        """
        time,text = zip(*self.data)
        iter_text = iter(text)
        y_values = [0]

        xdates = [datetime.datetime.strptime(time[0], "%a %b %d %X %z %Y")]
        current_epoch = xdates[0].timestamp()
        # TODO should be able to compare datetimes without converting to a number

        for counter, t in enumerate(time):
            # Convert time to number (seconds since epoch)
            t_epoch = datetime.datetime.strptime(t, "%a %b %d %X %z %Y").timestamp()
            # If time falls within time interval, add number to most recent y value
            if t_epoch - current_epoch < self.time_interval:
                y_values[-1] += addition_var(next(iter_text))
            else:
                current_epoch += (t_epoch-current_epoch)//self.time_interval*self.time_interval
                if counter != 0:
                    xdates.append(xdates[-1] + datetime.timedelta(seconds=self.time_interval))
                y_values.append(addition_var(next(iter_text)))

        return xdates, y_values

    def compute_volumes(self):
        """ Takes tweet data as input.
        Computes volumes of tweets per time period.
        Gives the list volumes with the number of tweets in each time interval given by the list xdates. 
        """

        def addition_var(text):
            return 1

        self.title = 'Volume'
        self.y_label = 'Number of tweets'
        return self.data_to_time_intervals(addition_var)

    def compute_sentiment_analysis(self):
        """ Takes tweet data as input.
        Computes sentiment analysis rating of tweet.
        Makes this into a pair of lists that can be graphed.
        """
        def addition_var(text):
            sentiment_num = 1 #Apply sentiment analysis to text to get a number
            return sentiment_num

        self.title = 'Sentiment Analysis'
        self.y_label = 'TODO'
        return self.data_to_time_intervals(addition_var)

    def plot(self,metric_func):
        """ Builds plot from Tweets ready for drawing or animating.
        x axis is time. metric_func creates time array, chooses what's shown on the y axis and creates y array.
        """
        y_values_lst = []
        xdates_lst = []
        for topic in self.topics:
            self.connect_to_db(topic)
            # Create self.data
            self.get_time_text_data()
            self.db.close()
            if self.data == []:
                print('WARNING: Nothing to plot')
                return
            else:
                # manipulate data
                tmp_xdates, tmp_y_values = metric_func()
                y_values_lst.append(tmp_y_values)
                xdates_lst.append(tmp_xdates)
        plt.cla()
        # Remove last datapoint since it represents a shorter length of time
        for counter, topic in enumerate(self.topics):
            plt.plot_date(xdates_lst[counter][:-1],y_values_lst[counter][:-1],'-',label=topic)
        plt.title(self.title+' of Tweets by Topic',fontsize=12)
        # plt.xlabel('Time')
        plt.ylabel(self.y_label+' per '+str(int(self.time_interval/60))+' Minutes')
        self.ax.xaxis.set_major_formatter(DateFormatter('%-d %b %H:%M'))
        self.ax.legend()
        # self.fig.autofmt_xdate()

    def instant_plot(self):
        """ Save plot of tweet data as png. """
        self.plot(metric_func=self.compute_volumes)
        plt.savefig('tweet_fig.png')

    def animate(self,i):
        """ Animation function for dynamic plot. """
        self.plot(metric_func=self.compute_volumes)
    def dynamic_plot(self):
        """ Dynamic plot of tweet data. """
        ani = animation.FuncAnimation(self.fig,self.animate,frames=self.frames,interval=self.time_interval*1000,repeat=False)
        # with open("corbyn_plot.html",'w') as file:
            # file.write(ani.to_html5_video())
        plt.show()
        self.animate(0)


if __name__ == '__main__':
    # minutes_total divided by minutes_interval must be an integer
    minutes_interval = 10
    minutes_total = 60
    topics = ['Corbyn', 'Brexit']
    plotter = PlotTweets(time_interval=int(minutes_interval*60),frames=int(minutes_total/minutes_interval),topics=topics)
    plotter.instant_plot()
    # plotter.dynamic_plot()