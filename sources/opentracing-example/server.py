#!/usr/bin/python           # This is server.py file
# coding=utf-8
import socket               
import helper
import opentracing
import zipkin_ot.tracer
import json

s = socket.socket()         	# create socket
host = socket.gethostname() 	# create host 
port = 12345                	
s.bind((host, port))        # bind port to host 
s.listen(5)	 				# wait for connection

def process_data(dish, dishes):	
	rate = 0
	for item in dishes:
		if helper.similar(dish, item['name']) == 1:
			suggest = None
			return ('Tên: ' + item['name'].encode('utf-8') + '\n' +
				'Địa điểm: ' + item['location'].encode('utf-8') + '\n' +
				'Loại: ' + item['type'].encode('utf-8') + '\n' +
				'Miêu tả: ' + item['description'].encode('utf-8'))
		elif helper.similar(dish, item['name']) > rate:
			suggest = item['name'].encode('utf-8')
			rate = helper.similar(dish, item['name'])
	if rate < 0.5:
		return 'Không tìm thấy món phù hợp !'
	elif suggest:
		return 'Ý bạn là: ' + suggest

if __name__ == '__main__':

	with zipkin_ot.Tracer(service_name = 'Tim kiem mon an-server',					# connect opantracing to zipkin server
		collector_host = 'localhost',
		collector_port = 9411,
		verbosity = 1) as tracer:
		opentracing.tracer = tracer
	while True:
		c, addr = s.accept()				# establish connection 
		print 'Got connection from', addr
		text_carrier = None
		dish_name = None
		while True:
			data = c.recv(2048)				# receive data from client
			if not data: 
				break
			try:
				text_carrier = json.loads(data)			# deserialize carrier
				if text_carrier:
					span_context = opentracing.tracer.extract(opentracing.Format.TEXT_MAP, text_carrier)
					with opentracing.tracer.start_span('process at server', child_of=span_context) as parent_span:
						carrier = {}
						opentracing.tracer.inject(parent_span.context, opentracing.Format.TEXT_MAP, carrier)
						with opentracing.start_child_span(parent_span, 'load csv file') as load_csv_span:
							monan = helper.loadCSV()
							load_csv_span.finish()
			except ValueError:
				text_carrier = None
				print 'Received:', data
				dish_name = data
			if dish_name and carrier and monan:
				span_ctx = opentracing.tracer.extract(opentracing.Format.TEXT_MAP, carrier)
				with opentracing.tracer.start_span('process data', child_of=span_ctx) as process_span:
					message = process_data(dish_name.decode('utf-8'), monan)			# process user input
					process_span.finish()
					parent_span.finish()
					dish_name = None
					c.send(message)