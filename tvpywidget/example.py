#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Vasya Zhirnov.
# Distributed under the terms of the Modified BSD License.

"""
TODO: Add module docstring
"""

import asyncio
import json
import logging
import socket
from threading import Thread
import time
from ipywidgets import DOMWidget
import tornado.websocket
from traitlets import Unicode, Int, Any
from ._frontend import module_name, module_version
from .vpython import GlowWidget, baseObj, canvas
from .rate_control import ws_queue

def find_free_port():
    print("looking for free port")
    s = socket.socket()
    s.bind(('',0)) # find an available port
    return s.getsockname()[1]

wsConnected = False

scene = None

class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("opening WS connection")
        global wsConnected
        wsConnected = True

    def on_message(self, message):
        ws_queue.put(message)

    def on_close(self):
        self.stop_tornado()

    def stop_tornado(self):
        ioloop = tornado.ioloop.IOLoop.instance()
        ioloop.add_callback(ioloop.stop)

    def check_origin(self, origin):
        return True

def start_server(_socket_port):
    print("starting tornado http server on port", _socket_port)
    asyncio.set_event_loop(asyncio.new_event_loop())
    print("spooling up event loop for asyncio")
    application = tornado.web.Application([(r'/ws', WSHandler),])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(_socket_port)
    Log = logging.getLogger('tornado.access')
    level = logging.getLevelName('WARN')
    Log.setLevel(level)
    tornado.ioloop.IOLoop.instance().start()

async def wsperiodic():
    while True:
        if ws_queue.qsize() > 0:
            data = ws_queue.get()
            d = json.loads(data)
            # Must send events one at a time to GW.handle_msg because
            # bound events need the loop code
            for m in d:
                # message format used by notebook
                msg = {'content': {'data': [m]}}
                baseObj.glow.handle_msg(msg)
        await asyncio.sleep(0.1)

# Removed check for ipykernel version because the old check
# was for 5.0.0 but this works with 4.x too...and 4.x is the first
# version of ipykernel
class ExampleWidget(DOMWidget):
    """TODO: Add docstring here
    """
    _model_name = Unicode('ExampleModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode('ExampleView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)
    _socket_port = find_free_port()

    value = Unicode('Hello World').tag(sync=True)
    wsport = Int(_socket_port).tag(sync=True)
    wsuri = Unicode("/ws").tag(sync=True)
    cmd = Any().tag(sync=True)
    
    t = Thread(target=start_server, args=(_socket_port,))
    t.start()
    print("started thread with socket handler")

    # initialize scene
    global scene
    scene = canvas()
    
    def __init__(self):
        super(ExampleWidget, self).__init__()
        # initialize scene
        # global scene
        # scene = canvas()
        
        # Setup ping pong
        # while (not wsConnected):
        #     print(wsConnected)
        #     time.sleep(1)          # wait for websocket to connect
        baseObj.glow = GlowWidget(wsport=self.wsport, wsuri='/ws', widget=self)

        baseObj.trigger()  # start the trigger ping-pong process
        loop = asyncio.get_event_loop()
        loop.create_task(wsperiodic())
 