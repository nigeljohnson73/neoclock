from _app.WeatherApi import getForecast

class NjDisplay:
    def __init__(self):
        self.btConnected(False)
        pass

    def loop(self):
        pass

    def btConnected(self, tf=None):
        if tf == None:
            return self.bt_connected

        self.bt_connected = tf

    def getForecast():
        return getForecast()
