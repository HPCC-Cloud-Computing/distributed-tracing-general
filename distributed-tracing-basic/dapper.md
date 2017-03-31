##1. Ý tưởng
   Ngày nay các hệ thống chủ yếu được thực hiện theo hệ thông phân tán với độ phưc tạp và khả năng mở rộng hệ thống lớn.  Các hệ thống này được xây dựng từ rất rất nhiều các thành phần nhỏ hơn và được phát triển bởi nhiều đội khác nhau và mỗi đội có thể lại sử dụng một ngôn ngữ. Chính vì vậy việc hiểu rõ sự vận hành và hành vi cuả cả hệ thông là rất quan trọng nhưng không dễ
Google dapper xây dựng nên để đáp ứng yêu cầu đó theo dấu hạ tầng của hệ thống.
 
##2. Key design
* Low overhead:  hệ thông theo dấu không nên có bất kì ảnh hưởng nào tới hiệu năng của chương trình.
* Application-level transparency:  lập trình viên không cần quan tâm hoặc không biết đến sự tồn tại của hệ thông theo dấu.
* Scalability: Việc theo dấu và tập hợp các theo dấu (tracing and trace collection) cần được xử lý kích thước, khả năng mở rộng của dịch vụ và các clusters.
 
##3. How to achieve key design(Cách để đạt được các key design)
Application-level transparency đạt được bằng cách hạn chế cá công cụ dò tìm cốt lõi của thằng dapper thay vào đó người ta dùng  tập hợp nhỏ các luồng phổ biến, kiểm soát dòng chảy và các thư viện RPC. Trong môi trường của google, tất cả ứng dụng sử dung chung các mô hình luồng, kiểm soát dòng chảy và hệ thống RPC nên việc hận chế các công cụ dò tìm thành các tập hợn các thư việc chung.
Scalability và low overhead đạt được bằng cách sử dụng các sampling. Người ta nhận thấy rằng một sample của 1 trong 1000 yêu cầu (request) cung cấp đủ thông tin cho việc theo dấu, truy tìm dữ liệu.
 
##4. Schema base for record information
1. Blackbox schemes: giả định không có thông tin bổ sung nào ngoài các tin nhắn đã được ghi lại, và sử dụng kỹ thuật thông kê hồi quy để suy luận kết luận (infer that asscociation).
2. Anotation base: dựa trên các ứng dụng và các phần mềm trung gian (middleware) để đánh dấu các bản lưu vs một định danh  (global indentifier) và cái định danh ấy sẽ kết nối dẫn tới nhưng tin nhắn được lưu và dẫn tới các request.
 
### So sánh blackbox schema và anotation base
   Black box thì nhỏ gọn di động hơn (portable) annotation based. Thằng annotation base cần nhiều dâta vì nó dựa trên thông kê nên data càng nhiều thì cang chính xấc. Bất lợi của thằng blackbox thì nó cần có các chương trình công cụ
 
##5. Trace trees and spans
   Dapper đánh dấu mỗi bản ghi vs một định danh (global identifier) và cái định danh ấy sẽ kết nối dẫn tới nhưng tin nhắn được lưu và dẫn tới các request. Trong cây dấu vêt Dapper (dapper trace tree) thì mỗi một node là một đơn vị cơ bản và đươc gọi là spans. Các cạnh chỉ ra một quan hệ bình thường giữa một spans con và spans cha. 
                        
##6. Implementation
    Mỗi thằng dapper trace sẽ biểu diễn ở dạng cây của các hoạt đông trên nhiều service. Mỗi trace sẽ được xác định bằng traceid của nó. Các nốt trên cây đc gọi là span. Nhà phát triển có thể cung cấp thêm cái thông tin theo dấu thông qua các chú thích. Để bảo vệ người dùng dapper khỏi việc vô tình lạm dụng việc loggin, thì mỗi caí thằng span trong traces đó sẽ có một giới hạn trên tổng số chú thích. Các chú thích không làm thay đổi cấu trúc của span hoặc thông tin RPC. Dữ liệu của span sẽ được ghi vào các file local log và sẽ đc lấy ra từ đây bởi Dapper daemon sau đó đc gửi qua các collection infrastructure và cuối cùng được viết vào trong BigTable.
