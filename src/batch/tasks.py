import os
from invoke import task


@task
def batch(c):
    collect_paths = os.listdir(path="/workspace/src/batch/collect/")
    calc_path = "/workspace/src/batch/calc/calc_recommend_list.py"
    exec_path = sorted(collect_paths)
    exec_path.append(calc_path)
    for path in exec_path:
        print(path)
        c.run(f"python3 {path}")
