import os
from invoke import task


@task
def batch(c):
    exec_paths = [
        "/workspace/src/batch/collect/collect01_retrieve_anime_list_page_html_for_each_initial.py",
        "/workspace/src/batch/collect/collect02_extract_changes.py",
        "/workspace/src/batch/collect/collect03_retrieve_anime_html.py",
        "/workspace/src/batch/collect/collect04_extract_data.py",
        "/workspace/src/batch/collect/collect05_retrieve_ongoing_anime_html.py",
        "/workspace/src/batch/calc/calc_recommend_list.py"
    ]
    for path in exec_paths:
        print(path)
        c.run(f"python3 {path}")
