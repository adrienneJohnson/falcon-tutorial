import os
import falcon

from .images import Collection, Item, ImageStore


def create_app(image_store):
  #Creates an instance of API that can be called from a WSGI server
  api = application = falcon.API()

  #add_route expects an instance of the resource, not the class
  api.add_route('/images', Collection(image_store))
  api.add_route('/images/{name}', Item(image_store))
  return api

def get_app():
  storage_path = os.environ.get('LOOK_STORAGE_PATH', '.')

  #create instance of ImageStore, which expects a storage path
  image_store = ImageStore(storage_path)
  return create_app(image_store)


