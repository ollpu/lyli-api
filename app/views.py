from urllib import quote_plus

from flask import jsonify, make_response, request, abort, render_template

from app import app
from app.urlshortener import URLShortener
from app.urlshortener.url import decodeURLPath, encodeURL, isValidScheme
from app.urlshortener.name import removeControlCharacters, isValidName

backend = URLShortener()

def getDefaultName():
    name = request.form.get('default_name', '')
    return backend.getNextName(name)

def bad_request(reason, code=400):
    return make_response(jsonify( { 'error': reason } ), code)

@app.route('/<name>', methods = ['GET'])
def visit(name):
    url = backend.visit(name)
    if url is None:
        abort(404)

    return jsonify({
            'short-url': 'http://lyli.fi/%s' % name,
            'url': url
        })

@app.route('/', methods = ['POST'])
def new():
    if not request.json:
        return bad_request('Data must be sent in json format')
    url = request.json.get('url', '')
    try:
        url = encodeURL(url)
    except:
        return bad_request('Could not encode URL')

    name = request.json.get('name', getDefaultName())
    name = decodeURLPath(name)
    name = removeControlCharacters(name)
    
    if url == '':
        return bad_request('No URL')
    
    elif not isValidScheme(url):
        return bad_request('Illegal scheme', 403)
    
    elif not isValidName(name):
        return bad_request('Illegal name', 403)
    
    elif not backend.shorten(url, name):
        return bad_request('Name is already in use', 403)
    
    return make_response(jsonify({
            'short-url': 'http://lyli.fi/%s' % quote_plus(name.encode('utf-8')),
            'url': url
        }), 201)

@app.route('/', methods = ['GET'])
def index():
    return render_template('index.html')

@app.errorhandler(404)
def notfound(error):
    return make_response(jsonify( { 'error': 'Not Found' } ), 404)

@app.errorhandler(500)
def eotfnund(error):
    return make_response(jsonify( { 'error': 'Internal Server Error' } ), 500)
