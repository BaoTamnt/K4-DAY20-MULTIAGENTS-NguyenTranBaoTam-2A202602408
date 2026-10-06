# Đánh giá skill do curator sinh

Curator được gọi hai lần, đều chỉ dùng `results/baseline` với `role=learn` và không có lỗi hạ tầng. Không đọc phản hồi eval. Không chỉnh sửa nội dung SKILL.md bằng tay.

Lần 1 sinh ba skill riêng cho type hints, regression tests và changelog. Bộ này đã được lưu nguyên trạng trong `curator-first-skills/`, cùng log `curator-first.txt`, rồi đưa ra khỏi `skills/auto/`. Lý do: skill regression sinh Python helper với mẫu `assert True`, không phát hiện regression; skill kiểm tra annotation bỏ qua tham số positional-only; cả bộ bỏ sót data/log. Skill changelog không có lỗi rõ ràng về quy ước nhưng dạng mã dài và thiếu bao phủ; lưu chung làm bằng chứng thay bộ.

Trước lần 2, cải thiện prompt curator để yêu cầu checklist, assertion thật và cân bằng loại tác vụ. Đây là thay đổi bộ tuyển chọn trước đóng băng, không phải sửa đầu ra skill. Lần 2 sinh ba skill ngắn và hợp lệ. Không gọi lần 3, không xóa skill nào của bộ thứ hai.

| Skill giữ lại | Tổng quát | Tính đúng và giới hạn | Description và độ dài |
|---|---|---|---|
| enforce-type-hints-on-public-functions | Dùng cho Python package mới, không nêu hàm hoặc đáp án của task học | Quy tắc annotation khớp detail. mypy là đề nghị kiểm chứng, không bảo đảm mọi kiểu được suy ra đúng; chưa cài mypy trong môi trường lab | Nêu rõ khi viết/review Python; checklist ngắn. Số dòng được tính tự động ở REPORT.md |
| write-meaningful-regression-tests-for-fixed-bugs | Dùng sau sửa bug bất kỳ; tên tests/test_regressions.py là quy ước được phép | Đã bỏ test rỗng, yêu cầu gọi hàm thật và input tái hiện lỗi. Một test mỗi bug không tự bảo đảm tối thiểu ba test nếu chỉ sửa ít bug; cần đối chiếu số bug thực tế | Kích hoạt rõ sau sửa bug; checklist ngắn; dùng file quy ước chung |
| parse-and-normalize-logs-for-error-reporting | Dùng cho log theo cấu trúc mức lỗi/traceback/lặp, không ghi đáp án hay tên tệp log học | Khớp quy tắc học về UTC, mức lỗi, tên service, sort và schema. Chưa quy định thuật toán phân đoạn rõ hoặc bắt buộc script; model vẫn có thể đếm tay sai. Schema 2 và generated_by là quy ước, không phải đáp án dataset | Kích hoạt cho structured error report, cụ thể đủ để chọn đọc; checklist dài nhất nhưng dưới giới hạn |

Hạn chế còn lại: bộ thứ hai vẫn không có skill cho báo cáo dữ liệu và không nhắc quy ước changelog. Đây là lỗi bao phủ của curator; giữ nguyên để đánh giá trung thực. Không thêm tay các quy ước bị thiếu. Nội dung quy ước từ detail học (tên tệp regression, schema_version, generated_by) được phép theo hướng dẫn 05; không có định danh riêng của eval và validate_skill trả về [] cho cả ba skill.

Việc đọc/áp dụng thực tế được đánh giá bằng `skills_read`, trace học thử và trace sau freeze. Chỉ đọc skill không đủ chứng minh đã làm đúng.
