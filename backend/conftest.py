import sys

# Prevent pyarrow C-extension access violation on Windows Python 3.13 during test collection
sys.modules["pyarrow"] = None
