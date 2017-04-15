# Dapper


## 1. Ý tưởng
Dapper được xây dựng dựa trên 2 mục tiêu cơ bản: sử dụng phổ biến và quản lý liên tục. Tính phổ biến rất quan trọng bởi vì sự hiệu quả của cơ sở hạ tầng theo dõi sẽ bị ảnh hưởng nếu một phần nhỏ của hệ thống không được quản lý. Thêm vào đó, việc quản lý cần phải được duy trì bởi vì sẽ có một vài thời điểm mà chúng ta không thể đoán được cách hệ thống vận hành và tái hiện quá trình đó. Từ 2 mục tiêu trên, Dapper phải đáp ứng được 3 yêu cầu tất yếu:

### 1.1. Chi phí thấp (low overheads):
Hệ thống truy vết không nên có bất cứ ảnh hưởng nào đến sự vận hành của hệ thống đang vận hành. 

### 1.2. Trong suốt ở mức úng dụng (application-level transparency):
Lập trình viên chỉ cần tập trung vào công việc của mình mà không cần bận tâm hay biết tới sự tồn tại của hệ thống truy vết.

### 1.3. Có khả năng mở rộng (Scalability):
Hệ thống này cần phải quản lý được khối lượng dịch vụ cực lớn của Google hiện nay và các cụm máy chủ cho ít nhất là vài năm nữa.
Một yêu cầu nữa cũng đáng chú ý là dữ liệu sau khi được truy vết (tracing) phải được sẵn sàng để  xử lý ngay sau khi được tạo ra: lý tưởng nhất là trong vòng 1 phút.

## Cách đạt được các key design
Application-level transparency, được cho là khó xây dựng nhất trong những yêu cầu kể trên, đạt được bằng cách hạn chế công cụ truy vấn chính sử dụng các thư viện không cần thiết mà thay vào đó là tập hợp các thư viện quản lý luồng, quy trình và RPC phổ biến. Trong hệ thống của Google, tất cả ứng dụng đều có sử dụng những thư viện giống nhau nên việc hạn chế công cụ truy vấn trong khuôn khổ của một số thư viện là điều hoàn toàn có thể làm được, sinh ra một công cụ truy vấn được coi trong suốt ở mức ứng dụng.
Khả năng mở rộng và chi phí thấp có thể đạt được bằng cách lấy mẫu truy vết một cách ngẫu nhiên chứ không nhất thiết phải lưu trữ và xử lý toàn bộ các dữ liệu truy vết. Ví dụ, trong mỗi 1000 mẫu dữ liệu truy vết, ta chỉ chọn ra 1 mẫu (tỉ lệ lấy mẫu - sampling rate) ở mức 0.1% là đủ để phản ánh phần nào hiện trạng của hệ thống cần truy vết. Tất nhiên, với tỉ lệ lấy mẫu như vậy, chúng ta chấp nhận việc mất mát thông tin từ các dữ liệu không được ghi nhận và xử lý.

## 2. Cách cài đặt
Dapper có khả năng theo dõi nhiều lối vận hành khác nhau mà không cần đến sự can thiệp từ những người phát triển và vận hành tầng ứng dụng (nhờ đặc tính trong suốt ở mực ứng dụng đã nói ở trên): 
* Khi một luồng xử lý một traced control path, Dapper đặt một trace context vào lưu trữ nội bộ của luồng. Trace context có thể hiểu là một đối tượng dữ liệu, dễ dàng copy của những tính chất của một nhịp.
* Khi việc tính toán được làm không đồng bồ, phần lớn lập trình viên của Google sử dụng một thư viện quản lý tiến trình để xây dựng những hàm callback và lưu lại việc nó sẽ được thực thi thế nào, vào thời điểm nào trong một bộ nhớ luồng hoặc trong những thành phần thực thi khác. Dapper đảm bảo rằng tất cả những hàm callback đó lưu lại trace context của tiến trình tạo ra nó, trace context này sẽ liên quan đến một luồng thích hợp khác khi hàm callback được thực thi. Bằng cách này, Dapper ids (được sử dụng để xây dựng lại truy vết) có khả năng theo dõi control paths không đồng bộ một cách trong suốt.
* Hầu hết việc trao đổi thông tin nội bộ trong một process của Google được xây dựng dựa trên một và chỉ một RPC framework được xây dựng từ C++ và Java. Framework này sẽ định nghĩa spans cho những RPCs khác có thể hiểu được. Những span và trace ids của RPC đang được truy vết sẽ truyền từ client đến server. Hệ thống dựa trên RPC như vậy đang được sử dụng rộng rãi tại Google. 

## 3.Tổ chức dữ liệu
Dapper được mô hình hóa bằng tree (cây), spans (nhịp) và annotation (chú thích). Trong cây truy vết (tree) các nốt được gọi là spans. Mũi tên nối giữa hai spans thể hiện mối quan hệ bình thường giữa span và span cha (parent span). Những span không có parent id được gọi là root span (gốc). Dù span nằm ở đâu trong tree thì span luôn lưu lại thời gian bắt đầu và kết thúc của span dưới dạng mã hóa.

Một điều quan trọng cần lưu ý nữa là span có thể bao gồm thông tin từ nhiều máy chủ, thực tế thì span chứa chú thích cho tiến trình của cả client và server. Và cũng vì thời gian của client và server khác nhau trên các máy nên chúng ta cần phải lưu ý về vấn đề clock skew(sự khác biệt thời gian). Một điều hiển nhiên là RPC client phải gửi request tới server thì server mới nhận được request và ngược lại server phải gửi phản hồi trước khi client nhận được phản hồi nên ta dễ dàng suy ra được giới hạn thời gian của span trên server.

Việc lưu lại các bản truy vết gồm 3 bước. 
Bước 1: dữ liệu của span sẽ được ghi vào file log cục bộ (local log file). 
Bước 2: dữ liệu đó sẽ được lấy ra từ các máy chủ đang vận hành.
Bước 3: dữ liệu cuối cùng được thêm vào một ô trong một của rất nhiều Dapper BigTable.
Mỗi truy vết sẽ được biểu diễn bởi một hàng trong Bigtable và mỗi cột tương ứng với một span. Thời gian trễ trung bình để dữ liệu truyền từ ứng dụng tới repository trung tâm ít hơn 15 giây. 

![Bigtable](bigtable.png) 

## 4. Đánh giá
*  Có lẽ một phần quan trọng nhất của cơ sở mã Dapper là các thiết bị đo đạc của RPC, luồng và đóng điều khiển các thư viện cơ bản, trong đó bao gồm cả việc tạo ra khoảng thời gian, lấy mẫu và khai thác bộ nhớ đĩa cục bộ. Bên cạnh dung lượng nhỏ, các mã này cần phải được ổn định và mạnh mẽ kể từ khi nó được liên kết thành một số lượng lớn các ứng dụng, làm cho việc bảo trì và sửa lỗi khó khăn. Các thiết bị đo đạc là ít hơn 1000 dòng mã trong C++ và dưới 800 dòng mã trong Java. Việc thực hiện chú thích các cặp khóa - giá trị (key - value) đã thêm 500 dòng mã.
* Thâm nhập Dapper có thể được đánh giá theo cả hai chiều: phần của quá trình sản xuất có thể tạo ra dấu vết Dapper ( ví dụ, những thứ được liên kết với Dapper- thư viện công cụ runtime) và phần của bộ máy sản suất chạy Dapper kết nối Dapper daemon là một phần của hình ảnh máy tính cơ bản của chúng tôi, làm cho nó xuất hiện hầu như tất cả máy chủ của Google. Rất khó để xác định các phần chính xác của các quá trình Dapper- sẵn sàng quá trình trước khi  các quá trình thông thường không có dấu vết thông tìn là vô hình với Dapper. Tuy nhiên, do sự phổ biến của thư viên Dappper, chúng tôi ước tính rằng gần như mọi quá trình sản xuất của Google đều hỗ trợ truy vết.
* Có những trường hợp Dapper không thể đi theo còn đường kiểm soát một cách chính xác. Chúng thường xuất phát tự việc sử dụng không đúng tiêu chuẩn kiểm soát dòng chảy, hoặc khi Dapper nhầm lẫn một thuộc tính quan hệ nhân quả không liên quan tới sự kiện. Dapper cung cấp một thư viện đơn giản giúp những nhà phát triển kiểm soát dấu viết theo cách như một công việc xung quanh.

## 5. References
[Benjamin H. Sigelman, Luiz André Barroso, Mike Burrows, Pat Stephenson, Manoj Plakal, Donald Beaver, Saul Jaspan, Chandan Shanbhag. 2010. Dapper, a Large-Scale Distributed Systems Tracing Infrastructure](https://research.google.com/pubs/pub36356.html)
