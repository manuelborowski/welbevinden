from app.data import photo as mphoto
import base64

def get_photo(id):
    photo = mphoto.get_first_photo({"id": id})
    return base64.b64encode(photo.photo)