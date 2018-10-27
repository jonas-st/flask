from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask.json import jsonify, dumps
from flask_cors import CORS
import datetime
import numpy as np

app = Flask(__name__)
api = Api(app)
CORS(app)

# ---- Weather App ----

# -- wetteranimation --
import re
from bs4 import BeautifulSoup
import urllib.request

url_temp = 'https://www.zamg.ac.at/cms/de/wetter/wetteranimation/aladin_animation.php?imgtype=0'
url_precip = 'https://www.zamg.ac.at/cms/de/wetter/wetteranimation/aladin_animation.php?imgtype=1'
url_cloud = 'https://www.zamg.ac.at/cms/de/wetter/wetteranimation/aladin_animation.php?imgtype=2'
re_animation = r'times\[[0-9]+\] = "(?P<date_string>.*) MESZ";\nimgnames\[[0-9]+\] = "(?P<url>.*)";'

def get_image_links(url):
    zamg_url_prefix = 'https://www.zamg.ac.at'

    fp = urllib.request.urlopen(url)
    mybytes = fp.read()
    data = mybytes.decode("utf8")
    fp.close()

    pattern = re.compile(re_animation)
    soup = BeautifulSoup(data, "html.parser")
    script = soup.find("script", text=pattern)

    date_strings = []
    urls = []


    if script:
        matches = pattern.finditer(script.text)
        for match in matches:
            date_string = match.group('date_string')
            url =  match.group('url')

            urls.append(zamg_url_prefix + url)
            date_strings.append(date_string)

    return urls, date_strings

# -- wetterkarten --
import datetime
import os

wetterkarten_url_format_string = 'http://www.zamg.ac.at/fix/wetter/bodenkarte/%04d/%02d/%02d/BK_BodAna_Sat_%02d%02d%02d%02d00.png'

def get_20_latest_wetterkarten_urls(url_format_string):
    urls = []

    current_datetime = datetime.datetime.now()

    if current_datetime.hour >= 0 and current_datetime.hour < 6:
        current_datetime = datetime.datetime(current_datetime.year,
                                             current_datetime.month,
                                             current_datetime.day,
                                             0,
                                             0)
    elif current_datetime.hour >= 6 and current_datetime.hour < 12:
        current_datetime = datetime.datetime(current_datetime.year,
                                             current_datetime.month,
                                             current_datetime.day,
                                             6,
                                             0)
    elif current_datetime.hour >= 12 and current_datetime.hour < 18:
        current_datetime = datetime.datetime(current_datetime.year,
                                             current_datetime.month,
                                             current_datetime.day,
                                             12,
                                             0)
    else:
        current_datetime = datetime.datetime(current_datetime.year,
                                             current_datetime.month,
                                             current_datetime.day,
                                             18,
                                             0)

    urls.append(url_format_string % (current_datetime.year,
                                         current_datetime.month,
                                         current_datetime.day,
                                         current_datetime.year-2000,
                                         current_datetime.month,
                                         current_datetime.day,
                                         current_datetime.hour))

    six_hours = datetime.timedelta(hours=6)

    for i in range(0,20):
        current_datetime = current_datetime - six_hours
        urls.append(url_format_string % (current_datetime.year,
                                             current_datetime.month,
                                             current_datetime.day,
                                             current_datetime.year-2000,
                                             current_datetime.month,
                                             current_datetime.day,
                                             current_datetime.hour))

    return urls

class Weather(Resource):
    def get(self):
        temp_urls, temp_dates = get_image_links(url_temp)
        precip_urls, precip_dates = get_image_links(url_precip)
        cloud_urls, cloud_dates = get_image_links(url_cloud)
        wetterkarten_urls = get_20_latest_wetterkarten_urls(wetterkarten_url_format_string)
        result = {"temp_urls": temp_urls,
                  "precip_urls": precip_urls,
                  "cloud_urls": cloud_urls,
                  "temp_dates": temp_dates,
                  "precip_dates": precip_dates,
                  "cloud_dates": cloud_dates,
                  "wetterkarten_urls": wetterkarten_urls
                  }

        return jsonify(result)




api.add_resource(Weather, '/weather') # Route_2

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=80)

