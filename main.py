import requests

EXAMPLE_URL = "https://file-examples.com/wp-content/uploads/2017/04/file_example_MP4_640_3MG.mp4"

def print_file_info(file_info):
    def get_pretty_file_size(sz_in_bytes):
        size_unit = ["B", "KB", "MB", "GB", "TB", "PB"]
        size_unit_i = 0 # default unit=B
        file_size = sz_in_bytes
        while file_size >= 1024:
            size_unit_i += 1 # change to next unit. i.e. B->KB
            file_size /= 1024
        return str(round(file_size, 2)) + " " + size_unit[size_unit_i]
        
    print("File type:", file_info["Content-Type"])
    print("File size:", get_pretty_file_size(file_info["File-Size"]))

def get_file_info(file_url, verbose=False):
    print("-> Gathering file information...", end="", flush=True)
    head_res = requests.head(file_url, proxies=None)
    assert head_res.status_code == 200 # make sure successful request
    res_info = head_res.headers
    if verbose: 
        print("HEAD-headers:", res_info)
    file_info = {"Accept-Ranges": "bytes", "Content-Length": 0, "Content-Type": ""}
    if all(required_attribs in res_info for required_attribs in file_info):
        for attrib_key in file_info:
            file_info[attrib_key] = res_info[attrib_key]
        file_info["File-Size"] = int(file_info["Content-Length"])
        print("Done")
        return file_info
    else:
        raise Exception("Failed to get file information. Aborted!")
        return None


def main():
    url = input("Enter url here: ")
    url = EXAMPLE_URL

    print_file_info(get_file_info(url))

if __name__ == "__main__":
    main() # run main routines