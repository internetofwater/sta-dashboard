import os
import subprocess

if_append = os.environ["APPEND_TO_EXISTING"].title() == 'True'
if if_append or not os.path.exists(
    os.path.join('sta_dashboard', 'data', os.environ["SQLITE_DB_FILENAME"])
    ):
    subprocess.run(['python3', 'db_cache.py'])
    
subprocess.run(['python3', 'app.py'])
