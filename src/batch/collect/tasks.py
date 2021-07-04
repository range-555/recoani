from invoke import task

file_list = [
    "01_retrieve_anime_list_page_html_for_each_initial.py",
    "02_extract_changes.py",
    "03_retrieve_anime_html.py",
    "04_extract_data.py",
    "05_retrieve_ongoing_anime_html.py",
    # もっと楽なロジックを考える(バッチ1回の遅れとかがあっても楽な方が良いかも)
    "04_extract_data.py"
]


@task
def collect(c):
    for f in file_list:
        c.run(f"python3 ./src/batch/collect/{f}")
