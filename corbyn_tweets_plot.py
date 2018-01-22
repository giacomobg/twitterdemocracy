import sqlite3
import datetime
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import seaborn as sns

class PlotTweets():
    """ Accesses a sqlite3 database containing tweet data and plots it.
    Use by running the plot() method."""
    def __init__(self,time_interval,frames):
        super(PlotTweets, self).__init__()
        self.time_interval = time_interval
        self.frames = frames
        attributes = {
            'axes.facecolor' : '#f0e6f2'
        }
        sns.set(context='paper',style='darkgrid',rc=attributes)
        self.fig, self.ax = plt.subplots()

    def connect_to_db(self):
        """ Connect to sqlite3 db with tweet data."""
        self.db = sqlite3.connect('tweets.db')

    def get_data(self):
        """ Retrieve tweet data from sqlite3 db. """
        cursor = self.db.cursor()
        # Retrieving text is currently unnecessary but will be used later
        cursor.execute('''SELECT tweet_time,tweet_text FROM tweets''')
        data = cursor.fetchall()
        return data

    def compute_volumes(self,data):
        """ Computes volumes of tweets per time period."""

        time,text = zip(*data)
        self.datetime = [datetime.datetime.strptime(time[0], "%a %b %d %X %z %Y")]

        time_epoch = [datetime.datetime.strptime(t, "%a %b %d %X %z %Y").timestamp() for t in time]

        iter_epoch = iter(time_epoch)
        next(iter_epoch)
        volume = [1]
        current_epoch = time_epoch[0]
        for t in iter_epoch:
            # add 1 to the appropriate entry in volume
            if t - current_epoch < self.time_interval:
                volume[-1] += 1
            else:
                current_epoch += (t-current_epoch)//self.time_interval*self.time_interval
                volume.append(1)
        return volume

    def plot(self):
        """ Builds plot ready for drawing or animating. """
        self.connect_to_db()
        data = self.get_data()
        if data != []:
            volume = self.compute_volumes(data)
            while len(self.datetime) < len(volume):
                # add time_interval seconds to datetime
                self.datetime.append(self.datetime[-1] + datetime.timedelta(seconds=self.time_interval))
            print(self.datetime)
            print(volume)
            self.db.close()
            plt.cla()
            plt.plot_date(self.datetime,volume,'-')
            plt.title('Volume of Jeremy Corbyn Tweets',fontsize=12)
            # plt.xlabel('Time')
            plt.ylabel('Number of Tweets per '+str(self.time_interval)+' Seconds')
            self.ax.xaxis.set_major_formatter(DateFormatter('%-d %b %H:%M'))
            self.fig.autofmt_xdate()

    def animate(self,i):
        """ Animation function for dynamic plot. """
        self.plot()

    def instant_plot(self):
        """ Save plot of tweet data as png. """
        self.plot()
        plt.savefig('tweet_volume.png')

    def dynamic_plot(self):
        """ Dynamic plot of tweet data. """
        ani = animation.FuncAnimation(self.fig,self.animate,frames=self.frames,interval=self.time_interval*1000,repeat=False)
        # with open("corbyn_plot.html",'w') as file:
            # file.write(ani.to_html5_video())
        plt.show()
        self.animate(0)


if __name__ == '__main__':
    # minutes_total divided by minutes_interval must be an integer
    minutes_interval = 0.05
    minutes_total = 1
    plotter = PlotTweets(time_interval=int(minutes_interval*60),frames=int(minutes_total/minutes_interval))
    plotter.dynamic_plot()