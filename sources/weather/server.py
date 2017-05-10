#!/usr/bin/python           # This is server.py file

import socket               # Import socket module
import json
import opentracing.tracer
import zipkin_ot

import coordinate
import weather

s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 12345                # Reserve a port for your service.
s.bind((host, port))        # Bind to the port

s.listen(5)                 # Now wait for client connection.

if __name__ == '__main__':

    with zipkin_ot.Tracer(service_name = 'Weather-server',	# connect opantracing to zipkin server
            collector_host = 'localhost',
            collector_port = 9411,
            verbosity = 1) as tracer:
            opentracing.tracer = tracer

    while True:
        c, addr = s.accept()     # Establish connection with client.
        print 'Got connection from', addr

        while True:
            data = c.recv(1024)
            #print "data ", data
            text_carrier = None
            address = None 
            if not data:
                break
            try:
                text_carrier = json.loads(data)
                if text_carrier:
                    # extract the text_carrier recive from client
                    span_context = opentracing.tracer.extract(opentracing.Format.TEXT_MAP, text_carrier)
                    # create child span of root span name server_span
                    # syntax opentracing.tracer.start_span(operation_name=XXX, child_of=YYY)
                    with opentracing.tracer.start_span('server process', child_of=span_context) as server_span:            
                        carrier = {}
                        opentracing.tracer.inject(server_span.context, opentracing.Format.TEXT_MAP, carrier)
                        #print 'carrier ', carrier
            except ValueError:
                text_carrier = None
                address = data
           
            if address and carrier:
                span_ctx = opentracing.tracer.extract(opentracing.Format.TEXT_MAP, carrier)
                # create child span of server_span  name getCoordinate_span
                with opentracing.tracer.start_span('get coordinate', child_of=span_ctx) as getCoordinate_span:
                    coordinateValue = coordinate.getCoordinate(address)
                    print "coordinateValue ", coordinateValue
                    lat = coordinateValue['lat']
                    lng = coordinateValue['lng']
                    #print 'lat and lng ', lat, lng
                
                # create child span of server_span  name getCoordinate_span
                with opentracing.tracer.start_span('get Weather infor', child_of=span_ctx) as getWeather_span:
                    weatherInfor = json.dumps(weather.getWeather(lat, lng))
                    #print weatherInfor
                    getWeather_span.finish()
                    server_span.finish()
                    address = None
                    c.send(weatherInfor)
        