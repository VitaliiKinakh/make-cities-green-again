from flask import Flask, request, send_from_directory, send_file
import json
app = Flask(__name__, static_url_path='')

def fek(cityName):
    return [1,2,3,4,600,700]

@app.route('/')
def main_mage(): 
    return send_file('index.html')

@app.route('/map/<city>')
def map_page(city): 
    return send_file('map.html')

@app.route('/city/<city>')
def get_images(city):
    city = city.replace('%20', ' ')
    
    result = fek(city)
    
    bingLink = "https://dev.virtualearth.net/REST/v1/Imagery/Map/Aerial?mapArea={},{},{},{}&mapSize={},{}&key=AnWCHN24sBudyTLhwXbYLYvwlnGhcIjB7len3DFbyyDDbU9z7JdMQFE81IiUNYhe".format(result[0], result[1], result[2], result[3], int(result[4]), int(result[5]))
    info = {'bingLink': bingLink, 'info': {'percent': 3, 'profit': 5, 'treeArea': 150, 'treeCount': 3123}}
    return json.dumps(info)

@app.route('/rgz/<city>')
def get_rgz(city):
    city = city.replace('%20', ' ')

    return send_file(filename, mimetype='image/png')

@app.route('/mgz/<city>')
def get_mgz(city):
    city = city.replace('%20', ' ')

    return send_file(filename, mimetype='image/png')

@app.route('/pgz/<city>')
def get_pgz(city):
    city = city.replace('%20', ' ')
    
    return send_file(filename, mimetype='image/png')

@app.route('/vpgz/<city>')
def get_vpgz(city):
    city = city.replace('%20', ' ')
    
    return send_file(filename, mimetype='image/png')

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
