#This # 01. Project Overview - Muanha

**Tên dự án:** Muanha Data Engine (Internal Name: Muanha)  
**Phiên bản hiện tại:** 3.2.0  
**Ngày cập nhật:** 20/04/2026  
**Owner:** Muanha Team

## Giới thiệu về Muanha

### Muanha là gì?

Muanha là một nền tảng để người dùng có thể xem giá nhà đất ở các quận huyện của Việt Nam nhưng phase đầu tiên sẽ tập trung vào TP.HCM. Người dùng có thể tìm kiếm theo các tiêu chí như giá cả, diện tích, số phòng ngủ, loại hình bất động sản, ...

### Đối tượng của Muanha là ai?

Người dùng có nhu cầu tìm hiểu về giá nhà đất.

### Nhiệm vụ của Muanha là gì?

Cung cấp cho người dùng thông tin về giá nhà đất ở các quận huyện của Việt Nam nhưng phase đầu tiên sẽ tập trung vào TP.HCM. Người dùng có thể tìm kiếm theo các tiêu chí như giá cả, diện tích, số phòng ngủ, loại hình bất động sản, ...

## 1. Mục tiêu kinh doanh (Business Objectives)

Muanha là nền tảng cung cấp thông tin về giá nhà đất, nhằm:

- Cung cấp cho người dùng thông tin về giá nhà đất ở các quận huyện của Việt Nam nhưng phase đầu tiên sẽ tập trung vào TP.HCM. Người dùng có thể tìm kiếm theo các tiêu chí như giá cả, diện tích, số phòng ngủ, loại hình bất động sản, ...

## 2. Stakeholders & User Persona

## 3. Phạm vi hiện tại (In-Scope / Out-of-Scope)

## 4. High-level Architecture (Tóm tắt)

Sourcecode này sử dụng Python technical stack chính cho Muanha.

- Dùng để viết script crawl data từ các nguồn data và ghi chép vào Supabase.
- Ở phase đầu tiên có thể sử dụng các nguồn đơn giản trước như nhatot.com, có thể phát triển crawl các nguồn phức tạp sau như batdongsan.com.vn, muaban.net, facebook, ...
- Trong thư mục database/db-schema.sql có chứa đoạn SQL để tạo database cho Muanha, hãy kiểm tra kỹ schema trước khi thực hiện bất kỳ tác vụ nào liên quan đến database.

- **Hướng dẫn sử dụng cho Agent:**

- Bạn là 1 Senior Data Engineer đang làm việc tại Muanha, bạn sẽ thực thi các tác vụ liên quan đến data engineering về giá nhà đất khu vực TPHCM.
- Nhiệm vụ của bạn là crawl data từ các nguồn data và ghi chép vào Supabase.
- File này là “single source of truth” về tổng quan dự án.
- Trước khi làm bất kỳ task nào liên quan đến feature mới hoặc thay đổi architecture, phải đọc file này cũng như là file README.md trước.
- Nếu phát hiện thông tin trong file này đã lỗi thời → báo cáo ngay và đề xuất cập nhật.
