from invoke import task

file_list = [
    "01_retrieve_anime_list_page_html_for_each_initial.py",
    "02_extract_changes.py",
    "03_retrieve_anime_html.py",
    "04_extract_anime_data.py",
    "05_extract_anime_cast.py",
    "06_extract_anime_staff.py",
    "07_extract_anime_other_information.py",
    "08_extract_anime_genre.py",
    "09_extract_related_anime.py",
    "10_extract_outline_each_episode.py",
    "11_retrieve_ongoing_anime_html.py",
    "10_extract_outline_each_episode.py",
    "12_copy_title_to_title_full.py"
]


@task
def collect(c):
    for f in file_list:
        c.run(f"python3 ./batch/{f}")
