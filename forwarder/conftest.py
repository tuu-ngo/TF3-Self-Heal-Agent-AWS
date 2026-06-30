import sys
from pathlib import Path

# cho phép `import alert_map` khi chạy pytest từ repo root hoặc forwarder/
sys.path.insert(0, str(Path(__file__).resolve().parent))
