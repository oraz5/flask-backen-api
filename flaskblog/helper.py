from flaskblog.routes import *
from pathlib import Path
import PIL
import json
import uuid
from uuid import UUID
import traceback
import jwt


def save_picture(form_picture, path):
    random_hex = secrets.token_hex(8)
    _ = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + '.webp'
    photo_path = app.root_path + path
    Path(photo_path).mkdir(parents=True, exist_ok=True)
    picture_path = os.path.join(photo_path, picture_fn)
    output_size = (1200, 800)
    i = PIL.Image.open(form_picture).convert('RGB')
    i.thumbnail(output_size, PIL.Image.ANTIALIAS)
    i.save(picture_path)
    return picture_fn

def save_picture_small(form_picture, path):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + '.webp'
    photo_path = app.root_path + path
    Path(photo_path).mkdir(parents=True, exist_ok=True)
    picture_path = os.path.join(photo_path, picture_fn)
    output_size = (250, 250)
    i = PIL.Image.open(form_picture).convert('RGB')
    i.thumbnail(output_size, PIL.Image.ANTIALIAS)
    i.save(picture_path)
    return picture_fn


# decorator for verifying the JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        print(request.headers)
        # jwt is passed in the request header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            print(token)
        # return 401 if token is not passed
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401
   
        try:
            print(app.config['SECRET_KEY'])
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
            print(data)
            current_user = Users.query\
                .filter_by(public_id = data['public_id'])\
                .first()
        except jwt.exceptions.ExpiredSignatureError as expired:
            print(expired)
            return jsonify({
                'message' : 'Token is expired !!'
            }), 401  
        except Exception as e:
            app.logger.info('api_add_cart error: %s', str(e)) 
            error = traceback.format_exc()
            print(error)
            return jsonify({
                'message' : 'Token is invalid !!'
            }), 401      
        # returns the current logged in users contex to the routes
        return  f(current_user, *args, **kwargs)
   
    return decorated


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)
