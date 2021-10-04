import os
import subprocess

if not os.path.exists(os.path.join('sta_dashboard', os.environ["SQLITE_DB_FILENAME"])):
    subprocess.run(['python', 'db_cache.py'])
    
subprocess.run(['python', 'app.py'])
