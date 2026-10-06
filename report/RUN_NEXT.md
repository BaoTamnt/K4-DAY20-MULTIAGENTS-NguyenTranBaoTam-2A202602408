# Chạy tiếp để hoàn tất sản phẩm nộp

Mã harness đã được cài đặt. Các bước dưới đây cần shell Linux/macOS hoặc WSL/Docker và cấu hình API thật trong `.env`. Không gửi hoặc commit khóa API.

1. Trong Linux, tạo môi trường riêng (không dùng `.venv` Windows):

```bash
python3 -m venv .venv-linux
source .venv-linux/bin/activate
pip install -e .
pytest
python scripts/tour.py
python -c "from lab.model import make_model; print(make_model().invoke('Reply with OK').content)"
```

2. Chạy học tuần tự, giữ nguyên tasks gốc:

```bash
python -m lab.runner --condition baseline --tasks learn
python -m lab.runner --condition subagents --tasks learn
python -m lab.curator
```

3. Đọc skill được sinh và điền mục 4–6 báo cáo từ kết quả thật. Nếu skill sai, xóa skill đó hoặc chạy lại curator theo giới hạn GUIDE; không sửa nội dung bằng tay. Sau khi bộ skill đạt yêu cầu:

```bash
python -m lab.runner --condition skills-auto --tasks learn
mv results/skills-auto results/skills-auto-dev
```

Chỉ dùng lệnh mv khi thư mục đích chưa tồn tại. Ghi nhận điểm học thử và rà lại H1–H3 dựa trên lỗi học; không xem check hoặc kết quả eval trước freeze.

4. Commit giả thuyết trước đóng băng (chỉ stage các sản phẩm lab, kiểm tra không chứa khóa):

```bash
git add src/lab/agent.py src/lab/subagents.py src/lab/runner.py src/lab/curator.py report skills/auto results
git commit -m "hypotheses"
git commit --allow-empty -m "freeze skills"
git tag freeze
```

5. Chạy chính thức, không thay đổi skills:

```bash
python -m lab.runner --condition baseline --tasks eval
python -m lab.runner --condition subagents --tasks eval
python -m lab.runner --condition skills-auto --tasks all
python scripts/verify_freeze.py
python -m lab.compare > report/table.md
python scripts/check_breakdown.py
```

6. Hoàn thiện báo cáo bằng số liệu trên, phân tích các check mới, token, skill đọc và nhiễu. Nếu lần chạy có `error`, xử lý nguyên nhân rồi chạy lại và ghi chú; không dùng lỗi hạ tầng làm kết luận về tác tử. Commit báo cáo/kết quả cuối sau khi `verify_freeze.py` báo OK.

Không tạo tag freeze trước khi có skill thật và giả thuyết chốt. `.venv-linux` là thư mục môi trường cục bộ, không đưa vào git.
