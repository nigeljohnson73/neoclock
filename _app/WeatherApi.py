import json
import os
import time
import threading
import requests
from _app.KillableThread import KillableThread


def runApi(key, location):

    if len(key) == 0 or len(location) == 0:
        print("WeatherApi: Skipping no configuration")
        return

    last_call = 0
    call_duration= 30
    print(f"WeatherApi: starting loop for '{location}'")
    while True:
        now = time.time()
        if now >= (last_call+call_duration):
            last_call = now
            outfile = os.path.join(".", "weather.json")
            data = {}

            if True:
                print ("Loading Weather API stored data")
                with open(outfile, 'r') as f:
                    data = json.load(f)
            else:
                print ("Making Weather API call")
                url = f"http://api.weatherapi.com/v1/forecast.json?key={key}&q={location}&days=1&aqi=yes&alerts=yes"
                print(f"    {url}")
                response = requests.get(url, stream=True)
                if response.ok:
                    print(f"    Response good")
                    data = json.loads(response.content)

                    with open(outfile,'w') as f:
                        json.dump(data, f, sort_keys = True, indent = 4, ensure_ascii = True)
                else:
                    print(f"    Response BAD")

            #for key in data:
                #print(key," : ",data[key]);

        time.sleep(0.1)
    print(f"WeatherApi: finishing loop for '{location}'")


class WeatherApi:
    def __init__(self, key, location):
        #self.thread = threading.Thread(target=runApi, args=(key, location,))
        self.thread = KillableThread(target=runApi, args=(key, location,))
        self.thread.start()

    def __del__(self):
        print("WeatherApi::__del__()")
        self.stop()

    def stop(self):
        print("WeatherApi::stop()")
        self.thread.kill()
        self.thread.join()
