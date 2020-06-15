from downloader import get_file_info, print_file_info, download_with_progress_bar, get_file_md5
from web_extractor import guess_type_of
from tkinter import filedialog

DEFAULT_CONNECTIONS = 2

EXAMPLE_URL = "https://file-examples.com/wp-content/uploads/2017/04/file_example_MP4_1920_18MG.mp4"
EXAMPLE_URL2 = "http://212.183.159.230/10MB.zip"


def print_intro() -> None:
    '''
    Print out program introduction
    '''
    print("==== Net-centric Programming HTTP Downloader ====")
    print("Author: hungthuanmk, tranduckhoatcu")
    print("Supported hosts:")
    print(" 1. Mediafire.com")
    print(" 2. Google Drive")
    print(" 3. Dropbox")
    print(" 4. Github")
    print(" 5. Youtube")
    print(" 6. Facebook Video")
    print(" 7. Any downloadable URL")
    print("-------------------------------------------------")


def main():
    print_intro()

    url = input("Enter URL here: ")

    try:
        print("-> Crawling...", end="", flush=True)
        file_url = guess_type_of(url)
        print("Done. File URL:", file_url)

        file_info = get_file_info(url)
        print_file_info(file_info)

        connections_count = input("Enter number of connections (default 2):")
        connections_count = DEFAULT_CONNECTIONS if len(
            connections_count) == 0 else int(connections_count)

        file_path = filedialog.askopenfilename(
            initialdir="/", title="Save file as", filetypes=(("jpeg files", "*.jpg"), ("All files", "*.*")))
        print(file_path)

        download_with_progress_bar(
            file_info, frames_count=connections_count, filename=file_path)
        print(" -> MD5: " + get_file_md5(file_path))
    except Exception as e:
        print("\n### There is an error occurred! ###")
        print(e)


if __name__ == "__main__":
    main()  # run main routines
