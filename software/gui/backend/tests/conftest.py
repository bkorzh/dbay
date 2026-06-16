import os

# Disable lab-link persistence before any backend module is imported, so tests
# never read or write the user's real state database.
os.environ["DBAY_PERSIST"] = "0"
