from flask import jsonify, make_response, request, abort

from app import app
from app.urlshortener import URLShortener
from app.urlshortener.url import decodeURLPath, encodeURL, isValidScheme
from app.urlshortener.name import removeControlCharacters, isValidName

backend = URLShortener()

def getDefaultName():
    name = request.form.get('default_name', '')
    return backend.getNextName(name)

def bad_request(reason):
    return make_response(jsonify( { 'error': reason } ), 400)

@app.route('/<name>', methods = ['GET'])
def visit(name):
    if name == '':
        abort(404)
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
        return bad_request('Illegal scheme')
    
    elif not isValidName(name):
        return bad_request('Illegal name')
    
    elif not backend.shorten(url, name):
        return bad_request('Name is already in use')
    
    return jsonify({
            'short-url': 'http://lyli.fi/%s' % name,
            'url': url
        })

@app.errorhandler(400)
def notfound(error):
    return make_response(jsonify( { 'error': 'Bad Request' } ), 400)

@app.errorhandler(404)
def notfound(error):
    return make_response(jsonify( { 'error': 'Not Found' } ), 404)

@app.errorhandler(500)
def eotfnund(error):
    return make_response(jsonify( { 'error': 'Internal Server Error' } ), 500)
