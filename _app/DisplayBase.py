from _app.WeatherApi import getForecast

'''
Base class that handles some data, but really is
just a holding spot for some inheritance on the 
loop function
'''


class DisplayBase:
    def __init__(self):
        self.btConnected(False)

    def __del__(self):
        pass

    def loop(self):
        pass

    def btConnected(self, tf=None):
        if tf == None:
            return self.bt_connected

        self.bt_connected = tf

    def getForecast():
        return getForecast()
