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

    def get_data(self):
        """ Retrieve tweet data from sqlite3 db. """
        cursor = self.db.cursor()
        # Retrieving text is currently unnecessary but will be used later
        cursor.execute('''SELECT tweet_time,tweet_text FROM tweets''')
        data = cursor.fetchall()
        return data

    def compute_volumes(self,data):
        """ Takes tweet data as input.
        Computes volumes of tweets per time period.
        Gives the list volumes with the number of tweets in each time interval given by the list xdates. 
        """

        time,text = zip(*data)
        xdates = [datetime.datetime.strptime(time[0], "%a %b %d %X %z %Y")]

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
                xdates.append(xdates[-1] + datetime.timedelta(seconds=self.time_interval))
                volume.append(1)
        return volume, xdates


    def plot_volume(self):
        """ Builds plot of volume of Tweets ready for drawing or animating. """
        volume_lst = []
        xdates_lst = []
        for topic in self.topics:
            self.connect_to_db(topic)
            data = self.get_data()
            self.db.close()
            if data == []:
                print('WARNING: Nothing to plot')
                return
            else:
                # Ensure tmp_xdates is of the correct length
                tmp_volume, tmp_xdates = self.compute_volumes(data)
                volume_lst.append(tmp_volume)
                xdates_lst.append(tmp_xdates)
        plt.cla()
        # Remove last datapoint since it represents a shorter length of time
        for counter, topic in enumerate(self.topics):
            plt.plot_date(xdates_lst[counter][:-1],volume_lst[counter][:-1],'-',label=topic)
        plt.title('Volume of Tweets by Topic',fontsize=12)
        # plt.xlabel('Time')
        plt.ylabel('Number of Tweets per '+str(int(self.time_interval/60))+' Minutes')
        self.ax.xaxis.set_major_formatter(DateFormatter('%-d %b %H:%M'))
        self.ax.legend()
        self.fig.autofmt_xdate()

    def animate(self,i):
        """ Animation function for dynamic plot. """
        self.plot_volume()

    def instant_plot(self):
        """ Save plot of tweet data as png. """
        self.plot_volume()
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
    minutes_interval = 5
    minutes_total = 60
    topics = ['Corbyn', 'Brexit']
    plotter = PlotTweets(time_interval=int(minutes_interval*60),frames=int(minutes_total/minutes_interval),topics=topics)
    plotter.dynamic_plot()