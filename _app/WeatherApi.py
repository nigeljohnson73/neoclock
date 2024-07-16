import datetime
import json
import os
import os.path
import time
import threading
import requests
from PIL import Image
from _app.KillableThread import KillableThread

forecast = {}

def runApi(key, location):
    global forecast

    if len(key) == 0 or len(location) == 0:
        print("WeatherApi: Skipping no configuration")
        return

    print(f"WeatherApi: starting loop for '{location}'")
    forecast = {"now":{}, "next":{}, "location":{}}
    forecast["valid"] = time.time()
    forecast["location"]["name"] = location
    forecast["now"]["temp_c"] = ""
    forecast["now"]["temp_f"] = ""
    forecast["now"]["humidity"] = ""
    forecast["now"]["condition_text"] = ""
    forecast["now"]["condition_icon"] = ""
    forecast["now"]["condition_img"] = None
    forecast["next"]["mintemp_c"] = ""
    forecast["next"]["mintemp_f"] = ""
    forecast["next"]["maxtemp_c"] = ""
    forecast["next"]["maxtemp_f"] = ""
    forecast["next"]["condition_text"] = ""
    forecast["next"]["condition_icon"] = ""
    forecast["next"]["condition_img"] = None

    last_call = 0
    last_hour = -1
    call_duration= 30
    while True:

        t = datetime.datetime.now().time()
        h = t.hour
        now = time.time()
        if h != last_hour or now >= (last_call+call_duration):
            last_call = now
            outfile = os.path.join(".", "weather.json")
            data = {}

            if h == last_hour and os.path.isfile(outfile):
                print ("Loading Weather API stored data")
                with open(outfile, 'r') as f:
                    data = json.load(f)
            else:
                last_hour = h
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

            print ("Weather API processing response")
            #for key in data:
                #print(key," : ",data[key]);
            forecast = {"now":{}, "next":{}, "location":{}}
            forecast["valid"] = time.time()
            forecast["location"]["name"] = data["location"]["name"]
            forecast["now"]["temp_c"] = data["current"]["temp_c"]
            forecast["now"]["temp_f"] = data["current"]["temp_f"]
            forecast["now"]["humidity"] = data["current"]["humidity"]
            forecast["now"]["condition_text"] = data["current"]["condition"]["text"]
            forecast["now"]["condition_icon"] = f'http:{data["current"]["condition"]["icon"]}'
            forecast["next"]["mintemp_c"] = data["forecast"]["forecastday"][0]["day"]["mintemp_c"]
            forecast["next"]["mintemp_f"] = data["forecast"]["forecastday"][0]["day"]["mintemp_f"]
            forecast["next"]["maxtemp_c"] = data["forecast"]["forecastday"][0]["day"]["maxtemp_c"]
            forecast["next"]["maxtemp_f"] = data["forecast"]["forecastday"][0]["day"]["maxtemp_f"]
            forecast["next"]["condition_text"] = data["forecast"]["forecastday"][0]["day"]["condition"]["text"]
            forecast["next"]["condition_icon"] = f'http:{data["forecast"]["forecastday"][0]["day"]["condition"]["icon"]}'
            try:
                forecast["now"]["condition_img"] = Image.open(requests.get(forecast["now"]["condition_icon"], verify=False, stream=True).raw)
            except:
                forecast["now"]["condition_img"] = None
            try:
                forecast["next"]["condition_img"] = Image.open(requests.get(forecast["next"]["condition_icon"], verify=False, stream=True).raw)
            except:
                forecast["next"]["condition_img"] = None

            print ("Weather API calls completed")
            #json_str = json.dumps(fc, indent=4)
            #print(json_str)


        time.sleep(0.1)
    print(f"WeatherApi: finishing loop for '{location}'")

def getForecast():
    global forecast
    return forecast

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
        global forecast
        forecast = {}
        self.thread.kill()
        self.thread.join()
