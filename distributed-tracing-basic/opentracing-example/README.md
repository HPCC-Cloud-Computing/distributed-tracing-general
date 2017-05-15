# Tìm kiếm món ăn

## 1. Mô tả hoạt động
1. Nhận input món ăn từ user và gửi lên server
2. Phía server chứa một số món ăn đặc sản trên các miền, nếu tên nhận được từ client được tìm thấy, server trả về thông tin món ăn đó. Còn không server sẽ trả về gợi ý về món ăn.
3. Client in ra response trả về từ server.

## 2. Cài đặt
1. Tải về docker [tại đây](https://www.docker.com/community-edition)
2. Khởi động Zipkin  `docker run -d -p 9411:9411 openzipkin/zipkin`
3. Tải về virtualenv `pip install virtualenv`
4. Khởi tạo môi trường test `virtualenv env`
5. Activate môi trường test `source env/bin/activate`
6. Cài đặt python packages trên môi trường test <br>`cd zipkin-python-opentracing` & `python setup.py install`
7. Chạy server `python server.py`, client `python client.py [host IP]`