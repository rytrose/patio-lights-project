from websocket_server import WebsocketServer

class LightController:
	def __init__(self):
		self.websocket_port = 8002
		self.server = WebsocketServer(self.websocket_port, host='0.0.0.0')
		self.server.set_fn_new_client(self.on_new_client)
		self.server.set_fn_client_left(self.on_client_left)
		self.server.set_fn_message_received(self.on_message)
		self.server.run_forever()

	def on_new_client(self, client, server):
		print("New client connected and was given id %d" % client['id'])

	def on_client_left(self, client, server):
		print("Client(%d) disconnected" % client['id'])

	def on_message(self, client, server, message):
		if len(message) > 200:
			message = message[:200] + '...'
		print("Client(%d) said: %s" % (client['id'], message))
		self.server.send_message_to_all("Hi Photon, from Pi!")

if __name__ == "__main__":
	print("Hello world!")
	lc = LightController()
