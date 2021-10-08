#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse, urlencode

def help():
  print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
  def __init__(self, code=200, body=""):
    self.code = code
    self.body = body

class HTTPClient(object):
  def get_host_port(self,url):
    # https://docs.python.org/3/library/urllib.parse.html
    # https://docs.oracle.com/en/storage/tape-storage/sl4000/slklg/default-port-numbers.html#GUID-8B442CCE-F94D-4DFB-9F44-996DE72B2558
    parsedurl = {}

    o = urlparse(url)

    if not o.scheme:
        o = urlparse('http://' + url)

    parsedurl['host'] = o.hostname
    parsedurl['port'] = o.port if o.port else 80 # default port if not specified
    parsedurl['path'] = o.path if o.path else '/' # default path if not specified

    return parsedurl

  def connect(self, host, port):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.connect((host, port))
    return None

  def get_code(self, data):
    # get response code
    # eg. get 301 from HTTP/1.1 301 Moved Permanently ...
    return int(data.split(' ')[1])

  def get_headers(self, data):
    # get all content before clrf
    clrf = "\r\n\r\n"
    return data.split(clrf)[0]

  def get_body(self, data):
    # get all content after first clrf
    clrf = "\r\n\r\n"
    return data.split(clrf, 1)[1]
  
  def sendall(self, data):
    self.socket.sendall(data.encode('utf-8'))
      
  def close(self):
    self.socket.close()

  # read everything from the socket
  def recvall(self, sock):
    buffer = bytearray()
    done = False
    while not done:
      part = sock.recv(1024)
      if (part):
        buffer.extend(part)
      else:
        done = not part
    return buffer.decode('utf-8')

  def GET(self, url, args=None):
    # Parse the url
    parsedurl = self.get_host_port(url)

    # Connect to the server
    self.connect(parsedurl['host'], parsedurl['port'])

    # Send request to the server
    request = f"GET {parsedurl['path']} HTTP/1.1\r\nHost: {parsedurl['host']}\r\nConnection: close\r\n\r\n"
    self.sendall(request)

    # Get response from the server
    response = self.recvall(self.socket)

    # Print response to std out
    print(response)

    # Get response parameters
    code = self.get_code(response)
    headers = self.get_headers(response)
    body = self.get_body(response)

    # Close the conenction
    self.close()

    # Return HTTP responce
    return HTTPResponse(code, body)

  def POST(self, url, args=None):
    # Parse the url
    parsedurl = self.get_host_port(url)

    # Connect to the server
    self.connect(parsedurl['host'], parsedurl['port'])

    # Parse arguments
    if args:
      req_body = urlencode(args)
    else:
      req_body = ''
    content_length = len(req_body.encode('utf-8'))

    # Send request to the server
    request = f"POST {parsedurl['path']} HTTP/1.1\r\nHost: {parsedurl['host']}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {content_length}\r\nConnection: close\r\n\r\n{req_body}"
    self.sendall(request)

    # Get response from the server
    response = self.recvall(self.socket)

    # Print response to std out
    print(response)

    # Get response parameters
    code = self.get_code(response)
    headers = self.get_headers(response)
    body = self.get_body(response)

    # Close the conenction
    self.close()

    # Return HTTP responce
    return HTTPResponse(code, body)

  def command(self, url, command="GET", args=None):
    if (command == "POST"):
      return self.POST( url, args )
    else:
      return self.GET( url, args )
    
if __name__ == "__main__":
  client = HTTPClient()
  command = "GET"
  if (len(sys.argv) <= 1):
    help()
    sys.exit(1)
  elif (len(sys.argv) == 3):
    print(client.command( sys.argv[2], sys.argv[1] ))
  else:
    print(client.command( sys.argv[1] ))
