import json
import io
import re
import os
import uuid
import mimetypes

import falcon
import msgpack

class Collection(object):

  def __init__(self, image_store):
    self._image_store = image_store

  def on_get(self, req, resp):
    doc = {
      'images': [
        {
          'href': '/images/8ee7480f-8de7-4ae5-a784-dfff7e57e611.png'
        }
      ]
    }

    resp.data = msgpack.packb(doc, use_bin_type=True)
    resp.content_type = falcon.MEDIA_MSGPACK
    resp.status = falcon.HTTP_200

  def on_post(self, req, resp):
    #calls save method on ImageStore which opens a file stream on the image sent in request and writes it to storage path
    name = self._image_store.save(req.stream, req.content_type)
    resp.status = falcon.HTTP_201
    resp.location = '/images/' + name

class Item(object):

  def __init__(self, image_store):
    self._image_store = image_store

  #parameters like 'name' specified in routes are turned into corresponding 'kwargs' (key word arguments)
  def on_get(self, req, resp, name):
    resp.content_type = mimetypes.guess_type(name)[0]

    #image is streamed out directly from open file using the open method
    #content length tells browser how much data to read from response
    resp.stream, resp.content_length = self._image_store.open(name)

    #response status defaults to 200

class ImageStore(object):

  _CHUNK_SIZE_BYTES = 4096
  _IMAGE_NAME_PATTERN = re.compile(
      '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.[a-z]{2,4}$'
  )

  def __init__(self, storage_path, uuidgen=uuid.uuid4, fopen=io.open):
    self._storage_path = storage_path
    self._uuidgen = uuidgen
    self._fopen = fopen

  def save(self, image_stream, image_content_type):
    ext = mimetypes.guess_extension(image_content_type)
    name = '{uuid}{ext}'.format(uuid=self._uuidgen(), ext=ext)
    image_path = os.path.join(self._storage_path, name)

    with self._fopen(image_path, 'wb') as image_file:
      while True:
        chunk = image_stream.read(self._CHUNK_SIZE_BYTES)
        if not chunk:
            break

        image_file.write(chunk)

    return name

  def open(self, name):
    #validate by pattern matching file name
    if not self._IMAGE_NAME_PATTERN.match(name):
      raise IOError('File not found')

    #create the path with the requested file name
    image_path = os.path.join(self._storage_path, name)

    #open the file
    stream = self._fopen(image_path, 'rb')

    #get the size of the file
    content_length = os.path.getsize(image_path)

    #return info to the image get request
    return stream, content_length



# class Resource(object):

#   _CHUNK_SIZE_BYTES = 4096

#   def __init__(self, storage_path):
#     self._storage_path = storage_path

#   def on_get(self, req, resp):
#     doc = {
#       'images': [
#         {
#           'href': '/images/1eaf6ef1-7f2d-4ecc-a8d5-6e8adba7cc0e.png'
#         }
#       ]
#     }
#     #json.dumps encodes object / json.loads for decoding
#     #resp.body = json.dumps(doc, ensure_ascii=False)

#     resp.data = msgpack.packb(doc, use_bin_type=True)

#     #A number of constants for common media types, including falcon.MEDIA_JSON, falcon.MEDIA_MSGPACK, falcon.MEDIA_YAML, falcon.MEDIA_XML, falcon.MEDIA_HTML, falcon.MEDIA_JS, falcon.MEDIA_TEXT, falcon.MEDIA_JPEG, falcon.MEDIA_PNG, and falcon.MEDIA_GIF
#     resp.content_type = falcon.MEDIA_MSGPACK

#     #Default, so not needed
#     resp.status = falcon.HTTP_200

#   def on_post(self, req, resp):
#     #get the extension
#     ext = mimetypes.guess_extension(req.content_type)

#     #create the uuid and generate the name from that and the extension. State syntax and then supply values for corresponding fields
#     name = '{uuid}{ext}'.format(uuid=uuid.uuid4(), ext=ext)

#     #create path from storage_path prop and name
#     image_path = os.path.join(self._storage_path, name)

#     #open a file and return a stream
#     with io.open(image_path, 'wb') as image_file:
#       while True:
#         #read the body of the request, limiting the bytes
#         chunk = req.stream.read(self._CHUNK_SIZE_BYTES)
#         if not chunk:
#           break

#         #writes the contents of string to the file, returning the number of characters written
#         image_file.write(chunk)

#     resp.status = falcon.HTTP_201
#     resp.location = '/images/' + name
