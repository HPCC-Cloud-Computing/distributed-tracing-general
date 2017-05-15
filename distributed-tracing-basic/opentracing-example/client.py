#!/usr/bin/python           # This is client.py file
# coding=utf-8
import socket             
import opentracing
import zipkin_ot.tracer
import json
import sys

with zipkin_ot.Tracer(service_name = 'Tim kiem mon an-client',			# config opentracing to zipkin server
	collector_host = 'localhost',
	collector_port =9411,
	verbosity = 1) as tracer:
	opentracing.tracer = tracer

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print '[Error] use: python client.py [host IP]!'
		exit()
	s = socket.socket()        # create socket
	host = sys.argv[1] 	# create host 
	port = 12345               

	s.connect((host, port))		# bind port to host

    # Use OpenZipkin's opentracing implementation

	while True:
		data = raw_input('Món ăn: ')		# get user input
		if not data: 
			break
		with opentracing.tracer.start_span(operation_name='Tim kiem mon an') as parent_span:

			with opentracing.start_child_span(parent_span, operation_name='Gui ten mon an') as child_span:
				text_carrier = {}
				opentracing.tracer.inject(parent_span.context, opentracing.Format.TEXT_MAP, text_carrier)
				with opentracing.start_child_span(parent_span, 'send text_carrier') as remote_span:
					message = json.dumps(text_carrier)
					s.send(message)
				s.send(data)
		print s.recv(2048)
		parent_span.finish()
	s.close()