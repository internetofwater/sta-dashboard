import os, json, subprocess


with open('endpoints.json') as f:
    ENDPOINTS = json.load(f)


if __name__ == '__main__':

    subprocess.run(['python3', 'db_cache.py'])
    subprocess.run(['python3', 'app.py'])
