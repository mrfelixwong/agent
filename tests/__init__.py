"""
Test suite for Meeting Agent
"""

import sys
from pathlib import Path

# Add src to path for testing
test_dir = Path(__file__).parent
src_dir = test_dir.parent / "src"
sys.path.insert(0, str(src_dir))