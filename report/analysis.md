# Phân tích kết quả và cơ chế

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
