from tkinter import filedialog


def asksaveasfile_csv_wrapper():
    file_name = filedialog.asksaveasfile(defaultextension=".csv")

    return file_name.name
