from flask import Flask, request, send_from_directory, send_file
import json
from Processor import Processor

app = Flask(__name__, static_url_path='')

# Global section
path_to_cities = "data/cities.shp"
path_to_dataset = "data/cities_database.json"
proc = Processor(path_to_cities_geom=path_to_cities, path_to_cities_info=path_to_dataset)


def get_city_info(city_name):
    return proc.get_city_info(city_name)


@app.route('/')
def main_page():
    return send_file('index.html')


@app.route('/map/<city>')
def map_page(city): 
    return send_file('map.html')


@app.route('/city/<city>')
def get_images(city):
    city = city.replace('%20', ' ')
    city = city.upper()
    result = get_city_info(city)
    bingLink = "https://dev.virtualearth.net/REST/v1/Imagery/Map/Aerial?mapArea={},{},{},{}&mapSize={},{}&key=AnWCHN24sBudyTLhwXbYLYvwlnGhcIjB7len3DFbyyDDbU9z7JdMQFE81IiUNYhe".format(result[0], result[1], result[2], result[3], int(result[4]), int(result[5]))
    city_stats = proc.get_city_stats(city)
    info = {'bingLink': bingLink, 'info': {'percent': city_stats["percentage"], 'profit': city_stats["profit"],
                                           'treeArea': city_stats["trees_area"], 'treeCount': city_stats["trees_count"]}}
    return json.dumps(info)


@app.route("/landsat/<city>")
def get_landsat_image(city):
    city = city.replace('%20', ' ')
    city = city.upper()

    if city in proc.cities_info.keys():
        if "raster_filename" in proc.cities_info[city].keys():
            return send_file(proc.cities_info[city]["raster_filename"])

    city_geom = proc.find_city_in_db(city)
    raster_filename = proc.get_raster_for_city(city_geom)
    return send_file(raster_filename, mimetype='image/tiff')


@app.route('/rgz/<city>')
def get_rgz(city):
    city = city.replace('%20', ' ')
    city = city.upper()
    green_zone_name = "rich_green_zone"
    _ = proc.process_city(city, green_zone_name)

    return send_file("data/images/" + city + green_zone_name + ".png", mimetype='image/png')


@app.route('/mgz/<city>')
def get_mgz(city):
    city = city.replace('%20', ' ')
    city = city.upper()
    green_zone_name = "medium_green_zone"
    mask = proc.process_city(city, green_zone_name)

    return send_file("data/images/" + city + green_zone_name + ".png", mimetype='image/png')


@app.route('/pgz/<city>')
def get_pgz(city):
    city = city.replace('%20', ' ')
    city = city.upper()
    green_zone_name = "poor_green_zone"
    mask = proc.process_city(city, green_zone_name)

    return send_file("data/images/" + city + green_zone_name + ".png", mimetype='image/png')


@app.route('/vpgz/<city>')
def get_vpgz(city):
    city = city.replace('%20', ' ')
    city = city.upper()
    green_zone_name = "very_poor_green_zone"
    mask = proc.process_city(city, green_zone_name)

    return send_file("data/images/" + city + green_zone_name +".png", mimetype='image/png')


@app.route('/js/<path>')
def static_js(path):
    return send_file('./js/'+path)


@app.route('/css/<path>')
def static_css(path):
    return send_file('./css/'+path)


@app.route('/img/<path>')
def static_img(path):
    return send_file('./img/'+path)


@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


if __name__ == '__main__':
   app.run()
