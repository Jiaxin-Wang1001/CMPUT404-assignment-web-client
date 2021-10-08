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
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostbyname(host)
        port = int(port)
        #print(host, port)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(data[0].split()[1])

    def get_headers(self,data):
        headers = ''
        for i in data[1:]:
            if not i:
                break
            headers = headers + i + '\r\n'
        return headers

    def get_body(self, data):
        i = 1
        while(data[i]):
            i += 1
        return data[i+1]
    
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
        code = 500
        body = ""
        url_parsed = urllib.parse.urlparse(url)
        # print(url_parsed)

        location = url_parsed.netloc
        # print("location", location)
        splited_location = location.split(':')
        host = splited_location[0]
        if len(splited_location) < 2:
            port = 80
        else:
            port = splited_location[1]
        path = url_parsed.path
        if not path:
            path = '/'
        if url_parsed.query:
            path += '?' + url_parsed.query
        

        self.connect(host, port)
        message = 'GET %s HTTP/1.1\r\n' % (path)
        host_name = 'Host: ' + location + '\r\n'
        user_agent = 'User-Agent: Not a agent\r\n\r\n'
        message = message + host_name + user_agent
        self.sendall(message)
        self.socket.shutdown(socket.SHUT_WR)
        data = self.recvall(self.socket)
        data = data.split('\r\n')
        #print('data is\n', data)
        code = self.get_code(data)
        body = self.get_body(data)
        #print("code is", code)
        #print("body is", body)
        self.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        url_parsed = urllib.parse.urlparse(url)
        #print(url_parsed)

        location = url_parsed.netloc
        splited_location = location.split(':')
        host = splited_location[0]
        if len(splited_location) < 2:
            port = 80
        else:
            port = splited_location[1]
        path = url_parsed.path
        # print("url_parsed", url_parsed)

        self.connect(host, port)
        message = 'POST %s HTTP/1.1\r\n' % (path)
        user_agent = 'User-Agent: An agent\r\n'
        data = []
        content_type = 'Content-Type: application/x-www-form-urlencoded\r\n'
        connection = 'Connection: close\r\n'
        if args != None:
            for i in args:
                name = i.replace(' ', '+')
                value = args[i].replace(' ', '+')
                data.append(name + '=' + value)
        data = '&'.join(data)
        length = str(len(data.encode()))
        content_length = 'Content-Length: ' + length + '\r\n'
        host_name = 'Host: ' + location + '\r\n'

        message = message + user_agent + host_name + content_type + content_length + connection + '\r\n' + data

        self.sendall(message)
        self.socket.shutdown(socket.SHUT_WR)
        data = self.recvall(self.socket)
        data = data.split('\r\n')
        #print('data is\n', data)
        code = self.get_code(data)
        body = self.get_body(data)
        
        self.close()

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
