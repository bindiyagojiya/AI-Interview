import os
import sys

# Configure SQLite for test suite execution to avoid external DB delays
os.environ["DATABASE_URL"] = "sqlite:///./test_interviewiq.db"

# Ensure backend root is on python path for tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
