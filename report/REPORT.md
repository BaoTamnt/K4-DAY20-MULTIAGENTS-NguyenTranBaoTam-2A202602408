# Báo cáo Lab: Self evolving Agentic


Trạng thái: đã có đủ 18 lần chạy chính thức, ba lần học thử với skill và các lần chẩn đoán lưu riêng.

## 1. Thông tin nhóm và cấu hình


| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Trần Bảo Tâm | 2A202602408 | Harness, subagents, runner, curator, thực nghiệm và báo cáo |


- Model: `openai:gpt-4.1-mini`; nhiệt độ 0.0; recursion_limit 60. Cùng cấu hình dùng cho ba điều kiện.

- Python 3.11.9; Deep Agents 0.7.21; LangChain 1.4.3; LangChain Core 1.6.6; LangChain OpenAI 1.6.7.

- Hệ điều hành Windows, shell Git sh. Backend có môi trường riêng, không kế thừa khóa API; hỗ trợ python3 qua python. Linux/macOS/WSL/Docker vẫn là môi trường chuẩn theo README.

- Số lần gọi tác vụ đã lưu: 24 = 18 chính thức + 3 học thử + 3 chẩn đoán. Curator ghi riêng ở `curator.txt`; probe kết nối dùng 11 token.

- Token tác vụ đã lưu: 800,344 chính thức + 249,664 học thử + 337,014 chẩn đoán. Không bao gồm token hai lần curator (không đo riêng), không suy ra chi phí USD từ tổng này.

- Commit xuất phát: `d982034811dae6e0e42d0698131a9f33972a0bed`; commit freeze: `a1aeaa4ae12f9bb35ed48c6b37267483d410b485`.

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
| code-eval | 0 | {} | 41658 | 0.90× | 15.4 |
| code-learn | 0 | {} | 65851 | 1.35× | 23.3 |
| data-eval | 1 | {'general-purpose': 1} | 63632 | 2.09× | 20.1 |
| data-learn | 1 | {'general-purpose': 1} | 43362 | 0.93× | 15.8 |
| logs-eval | 1 | {'general-purpose': 1} | 30538 | 1.37× | 21.1 |
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

## 7. Kết quả so sánh


| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 7/10 | 7/10 | 7/10 |
| data-learn | 5/8 | 2/8 | 5/8 |
| logs-learn | 1/9 | 1/9 | 1/9 |
| code-eval | 6/11 | 7/11 | 7/11 |
| data-eval | 5/9 | 2/9 | 5/9 |
| logs-eval | 1/10 | 1/10 | 6/10 |
| **Mean score - learning tasks** | 0.48 | 0.35 | 0.48 |
| **Mean score - evaluation tasks** | 0.40 | 0.32 | 0.60 |
| **Mean tokens per run** | 35,946 | 46,662 | 50,782 |
| **Runs that read a skill** | 0/6 | 0/6 | 0/6 |


| Điều kiện | Tập | Kỹ thuật | Quy ước | Token TB | Lần đọc skill |
|---|---|---|---|---|---|
| baseline | learn | 13/18 | 0/9 | 38,896 | 0/3 |
| baseline | eval | 12/18 | 0/12 | 32,996 | 0/3 |
| subagents | learn | 10/18 | 0/9 | 48,048 | 0/3 |
| subagents | eval | 10/18 | 0/12 | 45,276 | 0/3 |
| skills-auto | learn | 13/18 | 0/9 | 54,290 | 0/3 |
| skills-auto | eval | 18/18 | 0/12 | 47,274 | 0/3 |


Lỗi chính thức: không có trong các run đã lưu.

Skill bị sửa: [].

## 8. Phân tích


- Tập learn: baseline 0.479; subagents 0.354 (Δ -0.125); skills-auto 0.479 (Δ +0.000).

- Tập eval: baseline 0.400; subagents 0.320 (Δ -0.081); skills-auto 0.597 (Δ +0.197).

| Điều kiện | Điểm TB | Token TB | Giây TB | Điểm / 10k token |
|---|---|---|---|---|
| baseline | 0.440 | 35,946 | 17.8 | 0.1223 |
| subagents | 0.337 | 46,662 | 21.8 | 0.0721 |
| skills-auto | 0.538 | 50,782 | 17.9 | 0.1059 |

Hiệu quả điểm/token cao nhất ở baseline; chỉ là tỷ số cho bộ dữ liệu này, không phải định giá token hay kết luận về model nói chung.

Subagents đổi điểm eval -0.081, token TB gấp 1.30 baseline. Cần cân nhắc cả hai đại lượng; chi phí cao hơn không tự chứng minh chất lượng tốt hơn.


So sánh cùng bộ skill trước/sau freeze:

| Task học | Học thử | Chính thức | Δ điểm | Skill đọc thử | Skill đọc chính thức |
|---|---|---|---|---|---|
| code-learn | 7/10 | 7/10 | +0.000 | 0 | 0 |
| data-learn | 5/8 | 5/8 | +0.000 | 0 | 0 |
| logs-learn | 3/9 | 1/9 | -0.222 | 0 | 0 |


Các nhận xét về học dưới đây đã được viết trước đóng băng, chỉ dựa vào học. Phần đánh giá phía sau được bổ sung sau tag freeze; giả thuyết ở commit hypotheses không thay đổi.

Baseline: code 7/10, data 5/8, logs 1/9. Subagents: code 7/10, data 2/8, logs 1/9. Học thử với skill: code 7/10, data 5/8, logs 3/9. Cả ba lần học thử skills_read=0 và skills_modified=false. Do đó không thể quy cải thiện log cho việc đọc và áp dụng toàn bộ skill; frontmatter vẫn có thể tác động đến ngữ cảnh, ngoài nhiễu.

Code của subagents không giao việc lần nào. Data và logs mỗi bài giao một lần cho general-purpose, không phải ba subagent chuyên biệt. Lời giao data thiếu mốc UTC cụ thể, không nhắc cách hiểu date-only và không truyền đầy đủ yêu cầu distinct orders. Báo cáo subagent nói loại ba dòng trùng; tác tử chính đọc answer.json nhưng không tính lại từ nguồn. Đây là kiểm tra tồn tại tệp, chưa phải kiểm tra kết quả.

Lời giao logs nêu UTC, level, traceback và repeat_count khá đầy đủ nhưng không kèm toàn bộ mẫu JSON; báo cáo cuối không đủ để chứng minh parser đúng. Trace chỉ chứa luồng chính, không cho phép khẳng định subagent có hoặc không chạy script ở bên trong.

Trong baseline logs, chỉ đọc log rồi viết JSON bằng tay, không có execute để kiểm chứng. Năm check kỹ thuật ngoài valid_structure thất bại. Học thử với skill dùng script và tăng đúng số entry/múi giờ, nhưng cuối output lấy chuỗi `-- last message repeated 2 times --` làm exception và để repeat_count=1: chưa phân biệt dòng nhắc lặp với dòng cuối traceback.

Chốt bộ skill thứ hai nguyên trạng. Các giới hạn còn lại của curator được giữ và ghi ở skill-review.md; không bổ sung tay quy ước data/changelog.

### Check kỹ thuật và quy ước

Kết quả chính thức: baseline đạt 13/18 kỹ thuật trên học, 12/18 trên eval; subagents 10/18 ở cả hai tập; skills-auto 13/18 trên học và 18/18 trên eval. Tất cả điều kiện đạt 0/9 rule_ trên học và 0/12 rule_ trên eval. Như vậy phần tăng của skills-auto trên eval nằm hoàn toàn ở kỹ thuật, không ở quy ước mà curator định dạy.

Các quy ước eval mới, đọc sau đóng băng:

| Họ | Check mới | Quy tắc kiểm tra | Kết quả cả ba điều kiện |
|---|---|---|---|
| code | rule_version_bump | Tăng patch version một lần mỗi phiên sửa lỗi | Không đạt |
| data | rule_sorted_keys_format | answer.json có indent=2, sort_keys=True và newline cuối | Không đạt |
| logs | rule_source_line | Mỗi error có số dòng nguồn của entry | Không đạt |

Bộ skill chốt không chứa các quy tắc mới này. Các quy tắc kế thừa (type hints, regression tests, changelog; cents/meta/clean.csv; tên service/sort/schema) cũng không đạt. Bộ skill còn bỏ sót changelog và họ data ngay từ trước freeze.

### Đọc skill và bằng chứng cơ chế

Cả sáu lần chính thức skills-auto và ba lần học thử có skills_read=0, không có read_file trỏ vào skills/ trong trace. Kiểm tra ngoại tuyến bằng ScriptedChatModel cho thấy tên/description của cả ba skill và câu FIRST action đều có trong system prompt. Điều này loại trừ khả năng file chưa được loader nạp metadata, nhưng không chứng minh model đã đọc thân skill qua cách khác. Các trace không có lệnh shell đọc skill; cũng không giao task trong những lần skills-auto, nên không thấy bằng chứng truy cập thân skill ở subagent.

Không có check nào có thể được chứng minh là nhờ tác tử đọc và làm theo toàn bộ skill. Ví dụ dương chỉ ở mức tương quan: skills-auto/logs-eval đạt repeat_counts và counts_by_service, trong khi baseline không đạt; trace cho thấy tác tử đọc README rồi tạo parse_errors.py và chạy `python3 workspace/parse_errors.py`, thay cho viết JSON trực tiếp. Không được gọi đó là bằng chứng nhân quả của skill. Metadata có thể gợi ý cách làm, và nhiễu vẫn là giải thích khác.

Ví dụ skill không giúp: rule_type_hints và rule_regression_tests đều thất bại ở code-eval, dù hai description kích hoạt đúng loại tác vụ. Tác tử không đọc SKILL.md và chỉ sửa lỗi chức năng. rule_service_names, rule_sorted_errors và rule_schema_header ở logs-eval cũng thất bại dù checklist log có cả ba quy tắc; output vẫn theo cấu trúc đề bài mà thiếu quy ước tổ chức.

Code-eval của baseline đạt 6/7 kỹ thuật, bỏ negative_minutes_rejected. Subagents và skills-auto đạt 7/7. Trong trace skills-auto/code-eval, tác tử sửa billable_blocks để raise ValueError cho phút âm rồi chạy suite; đây là bằng chứng đọc docstring tốt hơn ở lần đó, không phải quy tắc từ skill.

### Giao việc và chi phí

Subagents không gọi các vai trò explorer/implementer/reviewer do nhóm định nghĩa. Hai bài code không giao việc; bốn bài data/logs mỗi bài gọi general-purpose một lần. Data-learn truyền thiếu mốc UTC và detail distinct orders. Data-eval truyền rõ UTC, dedup và missing sentinel hơn, nhưng vẫn đạt 2/9; không thể quy tất cả suy giảm cho thiếu prompt. Đọc answer.json sau báo cáo không thay thế tính lại từ dữ liệu nguồn. Trace không chứa nội bộ subagent nên chưa biết chính xác lỗi sinh ở bước nào.

Trên sáu task, subagents tốn token trung bình gấp 1,30 baseline nhưng điểm học giảm 0,125 và eval giảm khoảng 0,081. Trong thí nghiệm này không có lợi ích chất lượng để bù chi phí token. Baseline có tỷ số điểm/10.000 token tốt nhất (0,1223), skills-auto 0,1059 và subagents 0,0721. Skills-auto có điểm trung bình cao nhất nhưng tốn khoảng 1,41 lần token baseline. Đây là chỉ số so sánh nội bộ, không phải chi phí USD: token cached và token output có thể có giá khác nhau.

### Giả thuyết và nhiễu

- Với H1: phần dự báo chi phí tăng ít nhất 20% khớp với khoảng 30%; phần điểm eval bằng/cao hơn baseline không khớp, vì giảm khoảng 0,081.
- Với H2: chênh lệch điểm eval quan sát +0,197 vượt ngưỡng 0,10 dự đoán. Tuy nhiên không có đọc thân skill, không có rule_ được cải thiện và chỉ một lần chạy; chưa đủ kết luận một mức tăng đáng tin do skill tự sinh. Kết quả không xác nhận cơ chế chuyển giao quy ước đã dự đoán.
- Với H3: cải thiện học chính thức bằng 0, cải thiện eval khoảng +0,197, trái dự đoán mức tăng học lớn hơn eval. Không có dấu hiệu overfitting kiểu học tăng nhưng eval không tăng trong kết quả này; không suy ra skill tổng quát tốt vì thân skill chưa được đọc.

Cùng bộ skill, code-learn và data-learn giữ nguyên điểm trước/sau freeze; logs-learn giảm từ 3/9 xuống 1/9, chênh -2/9 ≈ -0,222. Trung bình ba task học giảm khoảng 0,074. Đây chỉ là dao động quan sát qua hai lần, không phải phương sai hay khoảng tin cậy. Chênh +0,197 ở eval chịu ảnh hưởng lớn của logs-eval (+5/10); dao động log học cho thấy không nên khẳng định nhân quả từ một lần chạy.

### Tính hợp lệ

Curator chỉ dùng feedback và trace của baseline học chính thức. Không đọc check/run eval trước freeze và không chạy lại curator sau freeze. Ba skill giữ nguyên byte/hash; sáu run chính thức có cùng hash và bắt đầu sau tag, skills_modified=false. verify_freeze.py báo OK. Việc đọc check eval để viết phân tích ở đây diễn ra sau freeze và không được đưa vào skill.

Không thấy định danh eval hoặc đáp án dataset trong skill. Tên tệp regression và schema log là quy ước chung được phép theo hướng dẫn 05. Có thiên lệch bao phủ từ curator: hai skill cho code, một cho logs, không có data. Đó là hạn chế của bước trừu tượng hóa, không phải bằng chứng rò rỉ eval.


Phân tích cơ chế từng check, quy ước mới và mức hỗ trợ H1–H3 được trình bày ở trên và lưu riêng trong `analysis.md`. Curator lọc role trước khi đọc trace; validate_skill kiểm tra marker; hash và freeze kiểm tra bộ skill. Không mở check/run eval trước freeze. Chênh lệch học–eval có thể do khác độ khó và quy ước, chưa đủ chứng minh overfitting một mình.

## 9. Hạn chế và tính hợp lệ


1. Chỉ ba task mỗi tập, không đại diện mọi loại việc; trung bình nhạy với một bài log thất bại.

2. Mỗi điều kiện chính thức chỉ chạy một lần, nhiệt độ 0 vẫn có nhiễu; không có khoảng tin cậy thống kê.

3. Quy ước ẩn do giảng viên thiết kế khiến skill có thể chuyển giao quy tắc mà không nâng năng lực suy luận tổng quát.

4. Chỉ một model và một môi trường Windows/Git sh; kết quả có thể thay đổi trên Linux hoặc model khác. Chuẩn hóa xuống dòng được áp dụng đồng nhất cho sandbox code.

5. Trace cắt từng message ở 1.500 ký tự và chỉ có luồng chính; thiếu nội bộ subagent và có thể thiếu đuôi script. Runner stream giữ trạng thái cuối khi lỗi nhưng không tái dựng mọi bước bên trong.

6. Các lần chạy chẩn đoán trước thí nghiệm làm tăng ngân sách; đã giữ riêng và không dùng làm phản hồi curator. Thử lại sau lỗi hạ tầng không được hiểu là chọn điểm tốt nhất.

## 10. Kết luận


Đã hoàn tất ba điều kiện trên sáu task, với kiểm thử ngoại tuyến đạt và quy trình freeze hợp lệ. Skills-auto có điểm eval cao nhất (0,597), baseline có điểm/token tốt nhất, còn subagents tốn thêm token nhưng giảm điểm trong lần chạy này. Không có lần đọc thân skill và không có rule_ đạt, nên chưa chứng minh lợi ích đến từ áp dụng skill tự sinh. Bước tiếp theo là lặp eval nhiều lần để ước lượng nhiễu và thử thêm model.

## Phụ lục


- Lệnh và thứ tự: `RUN_NEXT.md`; cấu hình không chứa key: `config.json`.

- Kiểm thử: `offline-tests.txt`; tour: `tour.txt`; freeze: `freeze-check.txt`; thống kê: `check-breakdown.txt`.

- Chẩn đoán: `results/diagnostics` và `results/debug`; baseline/skills chính thức không dùng những run này.

- [GPT-4.1 mini](https://developers.openai.com/api/docs/models/gpt-4.1-mini) được đối chiếu để chọn model hỗ trợ tool calling.

- VLearn yêu cầu đăng nhập và công cụ trình duyệt không khởi động được; chưa đọc nội dung trang riêng đó. Thực hiện dựa trên README/GUIDE/RUBRIC có trong kho và hướng dẫn của người học rằng tự tạo key/chọn model.
