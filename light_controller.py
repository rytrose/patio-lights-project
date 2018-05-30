from websocket_server import WebsocketServer
import OSC
import threading
import sys

class LightController:
	def __init__(self):
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

	def on_new_websocket_client(self, client, server):
		print("New client connected and was given id %d" % client['id'])

	def on_websocket_client_left(self, client, server):
		print("Client(%d) disconnected" % client['id'])

	def on_websocket_message(self, client, server, message):
		if len(message) > 200:
			message = message[:200] + '...'
		print("Client(%d) said: %s" % (client['id'], message))
		self.websocket_server.send_message_to_all("Hi Photon, from Pi!")

	def test_osc_handler(self, addr, tags, data, source):
		print(data)

if __name__ == "__main__":
	print("Hello world!")
	lc = LightController()
	


