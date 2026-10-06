# Thứ tự đã chạy và cách tái lập

Lab dùng OpenAI do người học tự cấp key, `LAB_MODEL=openai:gpt-4.1-mini`, nhiệt độ 0, recursion_limit 60. `.env` không được đưa vào git. Không cần Azure endpoint/deployment khi dùng cấu hình provider OpenAI.

## Cài đặt

Linux/macOS hoặc WSL/Docker là môi trường chuẩn theo README:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Windows của thí nghiệm có Python 3.11 và Git for Windows. Backend dùng sh.exe được tìm tương đối từ git.exe, hỗ trợ python3; chuẩn hóa xuống dòng chỉ trong bản sao Python của sandbox code. Không sử dụng Docker.

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e .
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
```

Các lệnh `python` dưới đây được thực hiện bằng `.venv/Scripts/python` trên Windows. `-X utf8` cần cho công cụ git đọc báo cáo tiếng Việt trên Windows.

```dotenv
OPENAI_API_KEY=<key riêng của người chạy>
LAB_MODEL=openai:gpt-4.1-mini
LAB_TEMPERATURE=0
```

## Trình tự thí nghiệm chính

```bash
python -m pytest -ra
python scripts/tour.py
python -c "from lab.model import make_model; print(make_model().invoke('Reply with OK').content)"
python -m lab.runner --condition baseline --tasks learn
python -m lab.runner --condition subagents --tasks learn
python -m lab.curator
```

Đã chạy curator hai lần: lưu bộ đầu tiên vào `report/curator-first-skills/` vì test rỗng và bỏ sót loại tác vụ, cải thiện prompt trong hàm được giao rồi gọi lại `python -m lab.curator`. Không sửa nội dung skill. Xem `skill-review.md`.

```bash
python -m lab.runner --condition skills-auto --tasks learn
```

Lưu ba lần học thử thành `results/skills-auto-dev/` trước khi chạy chính thức. Viết phân loại lỗi và H1–H3 chỉ từ học. Các bước git đã thực hiện:

```bash
git add src/lab/agent.py src/lab/subagents.py src/lab/runner.py src/lab/curator.py report results skills/auto
git commit -m hypotheses
git commit --allow-empty -m "freeze skills"
git tag freeze
```

Không chạy lại lệnh tạo tag trong kho hiện tại: tag đã tồn tại và xác định bộ skill của kết quả nộp. Để tái lập toàn bộ thí nghiệm mới, dùng checkout/thư mục độc lập và giữ kết quả cũ.

```bash
python -m lab.runner --condition baseline --tasks eval
python -m lab.runner --condition subagents --tasks eval
python -m lab.runner --condition skills-auto --tasks all
python -X utf8 scripts/verify_freeze.py
python -m lab.compare
python scripts/check_breakdown.py
python report/build_report.py
```

`report/build_report.py` tạo REPORT.md và table.md từ run.json, cấu hình, ghi chú và trace thật. `lab.compare` có sẵn là nguồn chuẩn của table.md. Báo cáo được cập nhật sau đánh giá; giả thuyết không thay đổi so với commit hypotheses.

## Lần chẩn đoán ngoài kết quả chính

1. data-learn đầu tiên chạm giới hạn 60 bước; lưu `results/diagnostics/data-learn-first`.
2. data-learn chẩn đoán 20 bước với runner stream giữ trace; lưu `results/debug/baseline/data-learn`. Trace cho thấy python3 chưa có, đường dẫn tuyệt đối và việc sửa dần lệnh.
3. code-learn trước xử lý CRLF đạt 6/10; lưu `results/diagnostics/code-learn-crlf`. File test không bị tác tử sửa nhưng CRLF khác hash LF gốc. Sau chuẩn hóa chỉ trong sandbox, chạy lại code-learn đạt 7/10 và giữ kết quả đó.

Curator không dùng các thư mục chẩn đoán. Số token của chúng được báo cáo riêng, không tính vào trung bình ba điều kiện.

## Kiểm tra bài nộp

```bash
python -m pytest
python -X utf8 scripts/verify_freeze.py
python -m lab.compare
python scripts/check_breakdown.py
git status --short
```

Nếu muốn chạy lại một task để nghiên cứu, dùng `--results results/replay` nhằm giữ nguyên các kết quả chính thức đã báo cáo. Cùng nhiệt độ 0 vẫn có thể có kết quả khác. Không đưa `.env`, môi trường ảo hoặc khóa API vào git.
