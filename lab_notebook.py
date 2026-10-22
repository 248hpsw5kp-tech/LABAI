from datetime import datetime

def log_experiment(text):
    with open("lab_notebook.txt", "a") as f:
        f.write(f"\n{datetime.now()} - {text}\n")
