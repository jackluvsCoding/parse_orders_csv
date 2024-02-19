import subprocess
from tkinter import filedialog


def asksaveasfile_csv_wrapper():
    file_name = filedialog.asksaveasfile(defaultextension=".csv")

    return file_name.name


def open_file_after_created(file):
    try:
        subprocess.call(("open", file))

    except Exception as e:
        raise Exception(e)
