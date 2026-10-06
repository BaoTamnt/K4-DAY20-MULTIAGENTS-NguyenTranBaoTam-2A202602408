# Báo cáo Lab: Self evolving Agentic


Trạng thái: bản trước đóng băng; chỉ phân tích những lần chạy đã có, chưa suy luận kết quả đánh giá.

## 1. Thông tin nhóm và cấu hình


| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Trần Bảo Tâm | 2A202602408 | Harness, subagents, runner, curator, thực nghiệm và báo cáo |


- Model: `openai:gpt-4.1-mini`; nhiệt độ 0.0; recursion_limit 60. Cùng cấu hình dùng cho ba điều kiện.

- Python 3.11.9; Deep Agents 0.7.21; LangChain 1.4.3; LangChain Core 1.6.6; LangChain OpenAI 1.6.7.

- Hệ điều hành Windows, shell Git sh. Backend có môi trường riêng, không kế thừa khóa API; hỗ trợ python3 qua python. Linux/macOS/WSL/Docker vẫn là môi trường chuẩn theo README.

- Số lần gọi tác vụ đã lưu: 12 = 6 chính thức + 3 học thử + 3 chẩn đoán. Curator ghi riêng ở `curator.txt`; probe kết nối dùng 11 token.

- Commit xuất phát: `d982034811dae6e0e42d0698131a9f33972a0bed`; commit freeze: `Chưa tạo (bản trước đóng băng)`.

- Mã bổ sung chỉ ở bốn module được giao; không thay đổi tests/tasks/scripts hoặc module có sẵn. Trên Windows, runner chuẩn hóa CRLF → LF chỉ trong bản sao Python của sandbox code để checker hash được byte gốc; trường workspace_lf_normalized ghi nhận việc này.

## 2. Giả thuyết (chốt trước tag freeze)


- H1 (subagents so với baseline): điểm đánh giá của subagents có thể bằng hoặc cao hơn baseline, nhưng token trung bình tăng ít nhất 20%. Vai trò reviewer giúp kiểm chứng; không tự suy ra được quy ước ẩn. Căn cứ: [Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system) ghi nhận chi phí đa tác tử cao, nhưng mức 15 lần của họ là so với chat, không phải dự báo cho baseline lab này.

- H2 (skills-auto so với baseline): kỳ vọng không có mức tăng đáng tin vượt 0,10 trên điểm đánh giá trung bình; tác tử có thể không đọc skill dù prompt yêu cầu, như đã quan sát ở học thử. Nếu có lợi thì chủ yếu ở rule_ kế thừa, không kỳ vọng đạt toàn bộ rule_ mới. [SkillsBench v1](https://arxiv.org/abs/2602.12670v1) cho thấy skill tự sinh không có lợi trung bình, phù hợp với dự đoán thận trọng này.

- H3 (tác vụ học so với tác vụ đánh giá): kỳ vọng mức tăng của skills-auto trên học lớn hơn mức tăng trên đánh giá; quy ước mới và dữ liệu mới giới hạn chuyển giao. [SkillEvolBench](https://arxiv.org/abs/2605.24117) ghi nhận thích nghi cục bộ thường không tạo ra kỹ năng tái sử dụng ổn định. So sánh thêm học thử và học sau freeze để kiểm tra nhiễu.

## 3. Làm quen Deep Agents


1. Tour quan sát chín công cụ: ls, read_file, write_file, edit_file, delete, glob, grep, execute, task. execute chạy shell; xem `tour.txt`.

2. general-purpose có các công cụ của tác tử chính; mỗi lần gọi mặc định stateless, chỉ nhận prompt được giao và trả báo cáo cuối. Baseline vẫn có general-purpose, nên không đồng nghĩa hoàn toàn không có khả năng giao việc.

3. Trích task: “Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report.” Trích execute: “Quote paths containing spaces (e.g. cd "/path/with spaces").” Tour ghi system prompt mặc định là chuỗi rỗng. Các prompt lab giữ nguyên; subagent nhận thêm PATHS_NOTE.

## 4. Đường cơ sở và phân loại lỗi


| Task học | Check thất bại | Nhóm | Bằng chứng detail |
|---|---|---|---|
| code-learn | rule_type_hints | E | RULE: every public function (name not starting with '_') in the package has type annotations on all parameters and on the return value. |
| code-learn | rule_regression_tests | E | RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3); the file must pass. |
| code-learn | rule_changelog | E | RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): <short description>' (at least 3 bullets). |
| data-learn | rule_money_in_cents | E | RULE: money values in answer.json are integer cents (1606.67 USD is written 160667). |
| data-learn | rule_meta_block | E | RULE: answer.json has an object `meta` = {"source": <input file name>, "rows_in": <number of data rows in the input file, duplicates included>, "rows_used": <number of distinct orders with a known amount>}. |
| data-learn | rule_clean_csv | E | RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents; one row per distinct order with a known amount; timestamp_utc as YYYY-MM-DDTHH:MM:SSZ (UTC); region in canonical spelling (North, South, East, West); amount in integer cents. |
| logs-learn | entry_count | D | wrong number of entries (got 19) |
| logs-learn | timestamps_utc | D | 8/25 timestamps match |
| logs-learn | exception_fields | D | 17 wrong `exception` values |
| logs-learn | repeat_counts | D | 17 wrong `repeat_count` values |
| logs-learn | counts_by_service | D | counts_by_service: wrong values |
| logs-learn | rule_service_names | E | RULE: service names in the output are lower-case with '-' replaced by '_' (payment-service -> payment_service). |
| logs-learn | rule_sorted_errors | E | RULE: `errors` is sorted by service, then by timestamp_utc, ascending. |
| logs-learn | rule_schema_header | E | RULE: the top-level object has "schema_version": 2 and "generated_by": "log-triage". |


Phân bố: {'E': 9, 'D': 5}. E là thiếu quy ước tổ chức; D là xử lý log, múi giờ, traceback hoặc lặp chưa đúng. Trace baseline logs-learn chỉ đọc log rồi viết JSON trực tiếp, không có execute để kiểm chứng: đây còn là bằng chứng hành vi B. Không quy toàn bộ lỗi cho A–D: code và data có các check kỹ thuật đạt, xem thống kê mục 7. Không thấy bằng chứng đủ để kết luận vá triệu chứng C hoặc báo cáo tệp không tồn tại F. Lỗi hash do CRLF ở lần code chẩn đoán không được phân loại như lỗi tác tử; bản LF có SHA-256 khớp hằng số checker.

## 5. Điều kiện subagents


explorer điều tra đặc tả và dữ liệu, không sửa; implementer triển khai và chạy kiểm tra; reviewer kiểm tra độc lập, không sửa. Description nêu rõ lúc gọi. Tác tử chính phải gửi đủ yêu cầu và đường dẫn, rồi kiểm tra báo cáo trả về.

| Task | Số giao việc | Loại được gọi trong trace | Token | So baseline | Giây |
|---|---|---|---|---|---|
| code-learn | 0 | {} | 65851 | 1.35× | 23.3 |
| data-learn | 1 | {'general-purpose': 1} | 43362 | 0.93× | 15.8 |
| logs-learn | 1 | {'general-purpose': 1} | 34932 | 1.63× | 35.0 |


Tên và số lần giao việc được trích từ tool task ở luồng chính; token callback tính cả subagent. Nội bộ subagent không nằm trong trace nên chỉ đánh giá được lời giao việc và báo cáo cuối, không khẳng định mọi bước nội bộ đã được kiểm chứng.

## 6. Self-evolving: skill do curator sinh


Curator chỉ dùng baseline learn không có error; có tên/detail check và cuối trace. Không dùng dữ liệu eval. Đầu ra giữ nguyên, không sửa tay. Chi tiết số lần sinh và quyết định giữ/xóa nằm trong `skill-review.md`.

| Skill | Tổng quát | Kiểm tra | Dòng thân | Description |
|---|---|---|---|---|
| enforce-type-hints-on-public-functions | Quy trình/quy ước rút từ phản hồi học; cần đối chiếu nội dung thực tế | Định dạng hợp lệ | 11 | Use this skill when reviewing or writing Python packages to ensure every public function (not starting with '_') has complete type annotations on all parameters and the return value. This improves code clarity, tooling support, and maintainability. |
| parse-and-normalize-logs-for-error-reporting | Quy trình/quy ước rút từ phản hồi học; cần đối chiếu nội dung thực tế | Định dạng hợp lệ | 24 | Use this skill to parse application log files and produce structured error reports. Extract only ERROR or CRITICAL entries, normalize timestamps to UTC ISO 8601 format, handle repeated messages, and aggregate counts by service with normalized service names. |
| write-meaningful-regression-tests-for-fixed-bugs | Quy trình/quy ước rút từ phản hồi học; cần đối chiếu nội dung thực tế | Định dạng hợp lệ | 12 | Use this skill when adding regression tests after fixing bugs. Write at least one test function per bug fixed, placing them in a dedicated regression test file. Tests must call real functions with meaningful assertions that verify the bug fix. |


Nhận xét về tính đúng và áp dụng từng quy tắc: xem `skill-review.md` và các trace skills-auto. Hợp lệ về cú pháp không chứng minh nội dung đúng. skills_read chỉ đếm skill khác nhau ở luồng chính, không đếm lại cùng skill.

## 7. Kết quả so sánh


| Task | baseline | subagents |
|---|---|---|
| code-learn | 7/10 | 7/10 |
| data-learn | 5/8 | 2/8 |
| logs-learn | 1/9 | 1/9 |
| **Mean score - learning tasks** | 0.48 | 0.35 |
| **Mean score - evaluation tasks** | - | - |
| **Mean tokens per run** | 38,896 | 48,048 |
| **Runs that read a skill** | 0/3 | 0/3 |


| Điều kiện | Tập | Kỹ thuật | Quy ước | Token TB | Lần đọc skill |
|---|---|---|---|---|---|
| baseline | learn | 13/18 | 0/9 | 38,896 | 0/3 |
| subagents | learn | 10/18 | 0/9 | 48,048 | 0/3 |


Lỗi chính thức: không có trong các run đã lưu.

Skill bị sửa: [].

## 8. Phân tích


Chưa chạy eval trước freeze. Những nhận xét so sánh đánh giá chỉ được bổ sung sau khi bộ skill và giả thuyết được đóng băng.


So sánh cùng bộ skill trước/sau freeze:

| Task học | Học thử | Chính thức | Δ điểm | Skill đọc thử | Skill đọc chính thức |
|---|---|---|---|---|---|
| code-learn | 7/10 | Chưa chạy | — | 0 | — |
| data-learn | 5/8 | Chưa chạy | — | 0 | — |
| logs-learn | 3/9 | Chưa chạy | — | 0 | — |


Phân tích cơ chế từng check, quy ước mới và mức hỗ trợ H1–H3 nằm trong `analysis.md` (điền từ trace thật sau đánh giá). Curator lọc role trước khi đọc trace; validate_skill kiểm tra marker; hash và freeze kiểm tra bộ skill. Không mở check/run eval trước freeze. Chênh lệch học–eval có thể do khác độ khó và quy ước, chưa đủ chứng minh overfitting một mình.

## 9. Hạn chế và tính hợp lệ


1. Chỉ ba task mỗi tập, không đại diện mọi loại việc; trung bình nhạy với một bài log thất bại.

2. Mỗi điều kiện chính thức chỉ chạy một lần, nhiệt độ 0 vẫn có nhiễu; không có khoảng tin cậy thống kê.

3. Quy ước ẩn do giảng viên thiết kế khiến skill có thể chuyển giao quy tắc mà không nâng năng lực suy luận tổng quát.

4. Chỉ một model và một môi trường Windows/Git sh; kết quả có thể thay đổi trên Linux hoặc model khác. Chuẩn hóa xuống dòng được áp dụng đồng nhất cho sandbox code.

5. Trace cắt từng message ở 1.500 ký tự và chỉ có luồng chính; thiếu nội bộ subagent và có thể thiếu đuôi script. Runner stream giữ trạng thái cuối khi lỗi nhưng không tái dựng mọi bước bên trong.

6. Các lần chạy chẩn đoán trước thí nghiệm làm tăng ngân sách; đã giữ riêng và không dùng làm phản hồi curator. Thử lại sau lỗi hạ tầng không được hiểu là chọn điểm tốt nhất.

## 10. Kết luận


Harness đã chạy bằng API thật; còn phần đánh giá chính thức sau đóng băng. Không kết luận về điểm eval khi chưa có dữ liệu.

## Phụ lục


- Lệnh và thứ tự: `RUN_NEXT.md`; cấu hình không chứa key: `config.json`.

- Kiểm thử: `offline-tests.txt`; tour: `tour.txt`; freeze: `freeze-check.txt`; thống kê: `check-breakdown.txt` khi đã chạy.

- Chẩn đoán: `results/diagnostics` và `results/debug`; baseline/skills chính thức không dùng những run này.

- [GPT-4.1 mini](https://developers.openai.com/api/docs/models/gpt-4.1-mini) được đối chiếu để chọn model hỗ trợ tool calling.

- VLearn yêu cầu đăng nhập và công cụ trình duyệt không khởi động được; chưa đọc nội dung trang riêng đó. Thực hiện dựa trên README/GUIDE/RUBRIC có trong kho và hướng dẫn của người học rằng tự tạo key/chọn model.
