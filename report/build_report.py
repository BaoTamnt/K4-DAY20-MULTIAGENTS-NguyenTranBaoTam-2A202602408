"""Generate the report from real run records; never invent missing results."""
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from statistics import mean

from lab.compare import build_table, load_runs
from lab.curator import validate_skill
from lab.tasks import ROOT

OUT = ROOT / "report"
CONDITIONS = ["baseline", "subagents", "skills-auto"]
runs = load_runs(ROOT / "results")
config = json.loads((OUT / "config.json").read_text(encoding="utf-8"))
official = {(r["condition"], r["task"]): r for r in runs}
dev = []
for p in sorted((ROOT / "results" / "skills-auto-dev").glob("*/run.json")):
    dev.append(json.loads(p.read_text(encoding="utf-8")))
diagnostics = []
for parent in [ROOT / "results" / "diagnostics", ROOT / "results" / "debug"]:
    for p in parent.rglob("run.json"):
        diagnostics.append(json.loads(p.read_text(encoding="utf-8")))
final = len(runs) == 18 and all(not r.get("error") for r in runs)

def trace(r):
    return (ROOT / "results" / r["condition"] / r["task"] / "trace.md").read_text(encoding="utf-8")

def table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
                     + ["| " + " | ".join(str(x).replace("|", "/").replace("\n", " ") for x in row) + " |" for row in rows])

def metrics(condition, role=None):
    rs = [r for r in runs if r["condition"] == condition and (role is None or r["role"] == role)]
    if not rs:
        return None
    return {"score": mean(r["score"] for r in rs), "tokens": mean(r["tokens"]["total"] for r in rs),
            "seconds": mean(r["seconds"] for r in rs)}

def breakdown():
    rows = []
    for c in CONDITIONS:
        for role in ["learn", "eval"]:
            rs = [r for r in runs if r["condition"] == c and r["role"] == role]
            if not rs:
                continue
            tech = [k for r in rs for k in r["checks"] if not k["name"].startswith("rule_")]
            rules = [k for r in rs for k in r["checks"] if k["name"].startswith("rule_")]
            rows.append([c, role, f"{sum(k['passed'] for k in tech)}/{len(tech)}",
                         f"{sum(k['passed'] for k in rules)}/{len(rules)}",
                         f"{mean(r['tokens']['total'] for r in rs):,.0f}",
                         f"{sum(r['skills_read'] > 0 for r in rs)}/{len(rs)}"])
    return table(["Điều kiện", "Tập", "Kỹ thuật", "Quy ước", "Token TB", "Lần đọc skill"], rows)

tag = subprocess.run(["git", "rev-parse", "freeze"], cwd=ROOT, capture_output=True, text=True)
freeze = tag.stdout.strip() if tag.returncode == 0 else "Chưa tạo (bản trước đóng băng)"
parts = ["# Báo cáo Lab: Self evolving Agentic\n",
         "Trạng thái: " + ("đã có đủ 18 lần chạy chính thức, ba lần học thử với skill và các lần chẩn đoán lưu riêng."
                             if final else "bản trước đóng băng; chỉ phân tích những lần chạy đã có, chưa suy luận kết quả đánh giá.")]
parts += ["## 1. Thông tin nhóm và cấu hình\n",
          table(["Họ tên", "Mã sinh viên", "Phần đóng góp"], [["Nguyễn Trần Bảo Tâm", "2A202602408", "Harness, subagents, runner, curator, thực nghiệm và báo cáo"]]),
          f"\n- Model: `{config['model']}`; nhiệt độ {config['temperature']}; recursion_limit {config['recursion_limit']}. Cùng cấu hình dùng cho ba điều kiện.",
          f"- Python {config['python']}; Deep Agents {config['packages']['deepagents']}; LangChain {config['packages']['langchain']}; LangChain Core {config['packages']['langchain-core']}; LangChain OpenAI {config['packages']['langchain-openai']}.",
          "- Hệ điều hành Windows, shell Git sh. Backend có môi trường riêng, không kế thừa khóa API; hỗ trợ python3 qua python. Linux/macOS/WSL/Docker vẫn là môi trường chuẩn theo README.",
          f"- Số lần gọi tác vụ đã lưu: {len(runs) + len(dev) + len(diagnostics)} = {len(runs)} chính thức + {len(dev)} học thử + {len(diagnostics)} chẩn đoán. Curator ghi riêng ở `curator.txt`; probe kết nối dùng 11 token.",
          f"- Commit xuất phát: `{config['starting_commit']}`; commit freeze: `{freeze}`.",
          "- Mã bổ sung chỉ ở bốn module được giao; không thay đổi tests/tasks/scripts hoặc module có sẵn. Trên Windows, runner chuẩn hóa CRLF → LF chỉ trong bản sao Python của sandbox code để checker hash được byte gốc; trường workspace_lf_normalized ghi nhận việc này."]
parts += ["## 2. Giả thuyết (chốt trước tag freeze)\n",
          "- H1 (subagents so với baseline): điểm đánh giá của subagents có thể bằng hoặc cao hơn baseline, nhưng token trung bình tăng ít nhất 20%. Vai trò reviewer giúp kiểm chứng; không tự suy ra được quy ước ẩn. Căn cứ: [Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system) ghi nhận chi phí đa tác tử cao, nhưng mức 15 lần của họ là so với chat, không phải dự báo cho baseline lab này.",
          "- H2 (skills-auto so với baseline): kỳ vọng không có mức tăng đáng tin vượt 0,10 trên điểm đánh giá trung bình; tác tử có thể không đọc skill dù prompt yêu cầu, như đã quan sát ở học thử. Nếu có lợi thì chủ yếu ở rule_ kế thừa, không kỳ vọng đạt toàn bộ rule_ mới. [SkillsBench v1](https://arxiv.org/abs/2602.12670v1) cho thấy skill tự sinh không có lợi trung bình, phù hợp với dự đoán thận trọng này.",
          "- H3 (tác vụ học so với tác vụ đánh giá): kỳ vọng mức tăng của skills-auto trên học lớn hơn mức tăng trên đánh giá; quy ước mới và dữ liệu mới giới hạn chuyển giao. [SkillEvolBench](https://arxiv.org/abs/2605.24117) ghi nhận thích nghi cục bộ thường không tạo ra kỹ năng tái sử dụng ổn định. So sánh thêm học thử và học sau freeze để kiểm tra nhiễu."]
parts += ["## 3. Làm quen Deep Agents\n",
          "1. Tour quan sát chín công cụ: ls, read_file, write_file, edit_file, delete, glob, grep, execute, task. execute chạy shell; xem `tour.txt`.",
          "2. general-purpose có các công cụ của tác tử chính; mỗi lần gọi mặc định stateless, chỉ nhận prompt được giao và trả báo cáo cuối. Baseline vẫn có general-purpose, nên không đồng nghĩa hoàn toàn không có khả năng giao việc.",
          '3. Trích task: “Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report.” Trích execute: “Quote paths containing spaces (e.g. cd "/path/with spaces").” Tour ghi system prompt mặc định là chuỗi rỗng. Các prompt lab giữ nguyên; subagent nhận thêm PATHS_NOTE.']
failures = []
groups = Counter()
for r in runs:
    if r["condition"] != "baseline" or r["role"] != "learn" or r.get("error"):
        continue
    for k in r["checks"]:
        if not k["passed"]:
            group = "E" if k["name"].startswith("rule_") else "D"
            groups[group] += 1
            failures.append([r["task"], k["name"], group, k.get("detail", "")])
parts += ["## 4. Đường cơ sở và phân loại lỗi\n",
          table(["Task học", "Check thất bại", "Nhóm", "Bằng chứng detail"], failures),
          f"\nPhân bố: {dict(groups)}. E là thiếu quy ước tổ chức; D là xử lý log, múi giờ, traceback hoặc lặp chưa đúng. "
          "Trace baseline logs-learn chỉ đọc log rồi viết JSON trực tiếp, không có execute để kiểm chứng: đây còn là bằng chứng hành vi B. "
          "Không quy toàn bộ lỗi cho A–D: code và data có các check kỹ thuật đạt, xem thống kê mục 7. Không thấy bằng chứng đủ để kết luận vá triệu chứng C hoặc báo cáo tệp không tồn tại F. "
          "Lỗi hash do CRLF ở lần code chẩn đoán không được phân loại như lỗi tác tử; bản LF có SHA-256 khớp hằng số checker."]
subrows = []
for r in runs:
    if r["condition"] == "subagents":
        names = re.findall(r'"subagent_type":\s*"([^"]+)"', trace(r))
        base = official.get(("baseline", r["task"]))
        ratio = r["tokens"]["total"] / base["tokens"]["total"] if base and base["tokens"]["total"] else 0
        subrows.append([r["task"], r["subagent_calls"], dict(Counter(names)), r["tokens"]["total"], f"{ratio:.2f}×", r["seconds"]])
parts += ["## 5. Điều kiện subagents\n",
          "explorer điều tra đặc tả và dữ liệu, không sửa; implementer triển khai và chạy kiểm tra; reviewer kiểm tra độc lập, không sửa. Description nêu rõ lúc gọi. Tác tử chính phải gửi đủ yêu cầu và đường dẫn, rồi kiểm tra báo cáo trả về.",
          table(["Task", "Số giao việc", "Loại được gọi trong trace", "Token", "So baseline", "Giây"], subrows),
          "\nTên và số lần giao việc được trích từ tool task ở luồng chính; token callback tính cả subagent. Nội bộ subagent không nằm trong trace nên chỉ đánh giá được lời giao việc và báo cáo cuối, không khẳng định mọi bước nội bộ đã được kiểm chứng."]
skillrows = []
for p in sorted((ROOT / "skills" / "auto").glob("*/SKILL.md")):
    text = p.read_text(encoding="utf-8")
    body = text.split("---", 2)[-1].strip()
    description = re.search(r"^description:\s*(.+)$", text, re.M)
    skillrows.append([p.parent.name, "Quy trình/quy ước rút từ phản hồi học; cần đối chiếu nội dung thực tế", 
                      "Định dạng hợp lệ" if not validate_skill(text, p.parent.name) else "KHÔNG HỢP LỆ",
                      len(body.splitlines()), description.group(1) if description else "Thiếu"])
parts += ["## 6. Self-evolving: skill do curator sinh\n",
          "Curator chỉ dùng baseline learn không có error; có tên/detail check và cuối trace. Không dùng dữ liệu eval. Đầu ra giữ nguyên, không sửa tay. Chi tiết số lần sinh và quyết định giữ/xóa nằm trong `skill-review.md`.",
          table(["Skill", "Tổng quát", "Kiểm tra", "Dòng thân", "Description"], skillrows),
          "\nNhận xét về tính đúng và áp dụng từng quy tắc: xem `skill-review.md` và các trace skills-auto. Hợp lệ về cú pháp không chứng minh nội dung đúng. skills_read chỉ đếm skill khác nhau ở luồng chính, không đếm lại cùng skill."]
comparison = build_table(runs)
(OUT / "table.md").write_text(comparison + "\n", encoding="utf-8")
parts += ["## 7. Kết quả so sánh\n", comparison, "\n" + breakdown()]
errors = [f"{r['condition']}/{r['task']}: {r['error']}" for r in runs if r.get("error")]
parts += ["\nLỗi chính thức: " + ("; ".join(errors) if errors else "không có trong các run đã lưu.")]
parts += ["Skill bị sửa: " + str([r["condition"] + "/" + r["task"] for r in runs if r["skills_modified"]]) + "."]
parts += ["## 8. Phân tích\n"]
if final:
    for role in ["learn", "eval"]:
        base = metrics("baseline", role)
        parts.append(f"- Tập {role}: baseline {base['score']:.3f}; " + "; ".join(
            f"{c} {metrics(c, role)['score']:.3f} (Δ {metrics(c, role)['score'] - base['score']:+.3f})"
            for c in ["subagents", "skills-auto"]) + ".")
    costrows = []
    for c in CONDITIONS:
        m = metrics(c)
        costrows.append([c, f"{m['score']:.3f}", f"{m['tokens']:,.0f}", f"{m['seconds']:.1f}", f"{m['score'] / m['tokens'] * 10000:.4f}"])
    parts.append(table(["Điều kiện", "Điểm TB", "Token TB", "Giây TB", "Điểm / 10k token"], costrows))
    best = max(CONDITIONS, key=lambda c: metrics(c)["score"] / metrics(c)["tokens"])
    parts.append(f"Hiệu quả điểm/token cao nhất ở {best}; chỉ là tỷ số cho bộ dữ liệu này, không phải định giá token hay kết luận về model nói chung.")
    delta = metrics("subagents", "eval")["score"] - metrics("baseline", "eval")["score"]
    ratio = metrics("subagents")["tokens"] / metrics("baseline")["tokens"]
    parts.append(f"Subagents đổi điểm eval {delta:+.3f}, token TB gấp {ratio:.2f} baseline. Cần cân nhắc cả hai đại lượng; chi phí cao hơn không tự chứng minh chất lượng tốt hơn.")
else:
    parts.append("Chưa chạy eval trước freeze. Những nhận xét so sánh đánh giá chỉ được bổ sung sau khi bộ skill và giả thuyết được đóng băng.")
if dev:
    noise = []
    for r in dev:
        later = official.get(("skills-auto", r["task"]))
        noise.append([r["task"], f"{r['passed']}/{r['total']}", f"{later['passed']}/{later['total']}" if later else "Chưa chạy",
                      f"{later['score'] - r['score']:+.3f}" if later else "—", r["skills_read"], later["skills_read"] if later else "—"])
    parts += ["\nSo sánh cùng bộ skill trước/sau freeze:", table(["Task học", "Học thử", "Chính thức", "Δ điểm", "Skill đọc thử", "Skill đọc chính thức"], noise)]
parts += ["\nPhân tích cơ chế từng check, quy ước mới và mức hỗ trợ H1–H3 nằm trong `analysis.md` (điền từ trace thật sau đánh giá). "
          "Curator lọc role trước khi đọc trace; validate_skill kiểm tra marker; hash và freeze kiểm tra bộ skill. "
          "Không mở check/run eval trước freeze. Chênh lệch học–eval có thể do khác độ khó và quy ước, chưa đủ chứng minh overfitting một mình."]
parts += ["## 9. Hạn chế và tính hợp lệ\n",
          "1. Chỉ ba task mỗi tập, không đại diện mọi loại việc; trung bình nhạy với một bài log thất bại.",
          "2. Mỗi điều kiện chính thức chỉ chạy một lần, nhiệt độ 0 vẫn có nhiễu; không có khoảng tin cậy thống kê.",
          "3. Quy ước ẩn do giảng viên thiết kế khiến skill có thể chuyển giao quy tắc mà không nâng năng lực suy luận tổng quát.",
          "4. Chỉ một model và một môi trường Windows/Git sh; kết quả có thể thay đổi trên Linux hoặc model khác. Chuẩn hóa xuống dòng được áp dụng đồng nhất cho sandbox code.",
          "5. Trace cắt từng message ở 1.500 ký tự và chỉ có luồng chính; thiếu nội bộ subagent và có thể thiếu đuôi script. Runner stream giữ trạng thái cuối khi lỗi nhưng không tái dựng mọi bước bên trong.",
          "6. Các lần chạy chẩn đoán trước thí nghiệm làm tăng ngân sách; đã giữ riêng và không dùng làm phản hồi curator. Thử lại sau lỗi hạ tầng không được hiểu là chọn điểm tốt nhất."]
parts += ["## 10. Kết luận\n",
          ("Đã hoàn tất ba điều kiện trên sáu task và lưu trace, token, điểm của từng lần chạy. "
           "Kết quả chỉ hỗ trợ kết luận trong phạm vi bộ lab và một model. "
           "Cần đọc cả điểm và chi phí, đồng thời phân biệt cải thiện quy ước với kỹ thuật. "
           "Bước tiếp theo là lặp eval nhiều lần để ước lượng nhiễu và thử thêm model."
           if final else "Harness đã chạy bằng API thật; còn phần đánh giá chính thức sau đóng băng. Không kết luận về điểm eval khi chưa có dữ liệu.")]
parts += ["## Phụ lục\n",
          "- Lệnh và thứ tự: `RUN_NEXT.md`; cấu hình không chứa key: `config.json`.",
          "- Kiểm thử: `offline-tests.txt`; tour: `tour.txt`; freeze: `freeze-check.txt`; thống kê: `check-breakdown.txt` khi đã chạy.",
          "- Chẩn đoán: `results/diagnostics` và `results/debug`; baseline/skills chính thức không dùng những run này.",
          "- [GPT-4.1 mini](https://developers.openai.com/api/docs/models/gpt-4.1-mini) được đối chiếu để chọn model hỗ trợ tool calling.",
          "- VLearn yêu cầu đăng nhập và công cụ trình duyệt không khởi động được; chưa đọc nội dung trang riêng đó. Thực hiện dựa trên README/GUIDE/RUBRIC có trong kho và hướng dẫn của người học rằng tự tạo key/chọn model."]
(OUT / "REPORT.md").write_text("\n\n".join(parts) + "\n", encoding="utf-8")
print(f"Report generated from {len(runs)} official records, {len(dev)} development records.")
