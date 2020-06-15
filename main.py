from downloader import get_file_info, print_file_info, download_with_progress_bar, get_file_md5

EXAMPLE_URL = "https://file-examples.com/wp-content/uploads/2017/04/file_example_MP4_1920_18MG.mp4"
EXAMPLE_URL2 = "http://212.183.159.230/10MB.zip"

def main():
    url = input("Enter url here: ")
    url = EXAMPLE_URL

    file_info = get_file_info(url)
    print_file_info(file_info)
    download_with_progress_bar(file_info, frames_count=2, filename="video.mp4")
    print(" -> MD5: " + get_file_md5("video.mp4"))
    # join_frames(None)
    

if __name__ == "__main__":
    main() # run main routines