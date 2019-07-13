from websocket_server import WebsocketServer
import OSC
import threading
import sys
import time
import json
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import random

class MyWebserverHandler(BaseHTTPRequestHandler):
	def _set_headers(self):
		self.send_response(200)
		self.send_header('Content-type', 'application/json')
		self.end_headers()

	def do_GET(self):
		self._set_headers()
		msg_dict = {
			'test_data': 999,
			'test_array': ["hi", "I'm", "Paul"]		
		}
		msg = json.dumps(msg_dict)
		self.wfile.write(msg)

class LightController:
	def __init__(self):
		# 10Hz, about max for websockets
		self.REFRESH_RATE = 0.025
		self.current_animation = None
		self.mode = "OFF"

		self.web_server_port = 8000
		self.web_server_thread = threading.Thread(target=self.start_webserver)
		self.web_server_thread.daemon = False
		# self.web_server_thread.start()

		self.websocket_port = 8002
		self.websocket_server = WebsocketServer(self.websocket_port, host='0.0.0.0')
		self.websocket_server.set_fn_new_client(self.on_new_websocket_client)
		self.websocket_server.set_fn_client_left(self.on_websocket_client_left)
		self.websocket_server.set_fn_message_received(self.on_websocket_message)
		self.websocket_server_thread = threading.Thread(target=self.websocket_server.run_forever)
		self.websocket_server_thread.daemon = False
		self.websocket_server_thread.start()

		self.osc_server = OSC.OSCServer(('127.0.0.1', 34567))
		self.osc_server_thread = threading.Thread(target=self.osc_server.serve_forever)
		self.osc_server_thread.daemon = False
		self.osc_server_thread.start()
		self.osc_server.addMsgHandler("/test", self.test_osc_handler)

		self.osc_client = OSC.OSCClient()
		self.osc_client.connect(('192.168.86.127', 34568))

		self.current_light_array = [[0, 0, 0, 0] for i in range(1)] # to be 60 * 15

		self.light_driver_thread = threading.Thread(target=self.light_driver)
		self.light_driver_thread.daemon = False
		self.light_driver_thread.start()

		self.changeModes("RED_RAMP")

	def start_webserver(self, server_class=HTTPServer, handler_class=MyWebserverHandler, port=8000):
		server_address = ('192.168.86.128', port)
		httpd = server_class(server_address, handler_class)
		httpd.serve_forever()

	def on_new_websocket_client(self, client, server):
		print("New client connected and was given id %d" % client['id'])

	def on_websocket_client_left(self, client, server):
		print("Client(%d) disconnected" % client['id'])

	def on_websocket_message(self, client, server, message):
		print("Client(%d) said: %s" % (client['id'], message))
		res = json.loads(message)
		self.changeModes(res['ani'])

	def test_osc_handler(self, addr, tags, data, source):
		print(data)

	def light_driver(self):
		while True:
			if(self.current_animation):
				self.current_light_array = self.current_animation.next()
				msg_dict = {
					'light_array' : self.current_light_array
				}
				msg = json.dumps(msg_dict)
				print(msg)
				# self.websocket_server.send_message_to_all(msg)
				msg = OSC.OSCMessage()
				msg.setAddress("/test")
				msg.append(random.randint(-1000, 1000))
				self.osc_client.send(msg)
			else:
				msg_dict = {
					'light_array' : [[0, 0, 0, 0]]
				}
				msg = json.dumps(msg_dict)
				print(msg)
				msg = OSC.OSCMessage()
				msg.setAddress("/test")
				msg.append(random.randint(-1000, 1000))
				self.osc_client.send(msg)
				# self.websocket_server.send_message_to_all(msg)
			time.sleep(self.REFRESH_RATE)

	def changeModes(self, mode):
		if mode == "RED_RAMP":
			print("Changing mode to RED_RAMP")
			self.current_animation = TestAnimation(self.REFRESH_RATE)
		elif mode == "OFF":
			print("Changing mode to OFF")
			self.current_animation = None
		else:
			print("Unknown mode {0}".format(mode))

class TestAnimation:
	def __init__(self, refresh_rate):
		self.REFRESH_RATE = refresh_rate
		self.ctr = 0
		self.r = 255
		self.light_array = [[255, 0, 0, 255] for i in range(1)] # to be 60 * 15

	def next(self):
		if self.ctr < 0:
			self.ctr += 1
			return self.light_array
		else:
			if self.r == 0:
				self.r = 255
			else:
				self.r -= 1

			for i, rgba in enumerate(self.light_array):
				self.light_array[i][0] = self.r

			self.ctr = 0
			return self.light_array

if __name__ == "__main__":
	print("Hello world!")
	lc = LightController()
	


