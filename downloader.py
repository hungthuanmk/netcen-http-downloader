import os
import time
import threading
import requests
import hashlib
from tqdm import tqdm

def print_file_info(file_info: dict) -> None:
    def get_pretty_file_size(sz_in_bytes: int) -> str:
        """
        This function converts size in bytes to suitable size unit (size < 1024)

        Parameters:
        ---
        file_info (dict): dict of file information came from get_file_info function

        Return: 
        ---
        A string with unit included
        >>> get_pretty_file_size(1024) = 1 KB
        """
        size_unit = ["B", "KB", "MB", "GB", "TB", "PB"]
        size_unit_i = 0 # default unit=B
        file_size = sz_in_bytes

        while file_size >= 1024: # convert until < 1024
            size_unit_i += 1 # change to next unit. i.e. B->KB
            file_size /= 1024 # get corresponded size in next unit
        return str(round(file_size, 2)) + " " + size_unit[size_unit_i]
    
    print("File type:", file_info["Content-Type"])
    print("File size:", get_pretty_file_size(file_info["Content-Length"]))


def get_file_info(file_url: str, verbose: bool = False, proxies: dict = None) -> dict:
    """
    Get file information in headers from a HEAD request
    """
    print("\n-> Gathering file information... ", end="", flush=True)
    head_res = requests.head(file_url, proxies=proxies)
    assert head_res.status_code == 200 # make sure successful request
    res_info = head_res.headers # take info from "head"-request headers
    if verbose: 
        print("HEAD-headers:", res_info)

    file_info = {"Accept-Ranges": "bytes", "Content-Length": 0, "Content-Type": ""} # required attributes
    if all(required_attribs in res_info for required_attribs in file_info): # make sure all required attributes are present
        for attrib_key in file_info:
            file_info[attrib_key] = res_info[attrib_key]
        file_info["Content-Length"] = int(file_info["Content-Length"])
        file_info["File-URL"] = file_url
        print("Done")
        return file_info
    else:
        raise Exception("Failed to get file information. Aborted!")
        return None


def join_frames(filename: str, frames_count: int, delete_frames: bool = True) -> None:
    print("\n-> Joining {} downloaded frames...".format(frames_count), end="")
    with open(filename, "wb") as target_file:
        for i in range(frames_count):
            with open("{}.part{}".format(filename, str(i)), "rb") as f:
                target_file.write(f.read())
    print("Done")
    if delete_frames:
        print("-> Removing temporary files...", end="", flush=True)
        for i in range(frames_count):
            os.remove("{}.part{}".format(filename, str(i)))
        print("Done")
    


def download_with_progress_bar(file_info: dict, frames_count: int=12, filename: str="temp", verbose=False):
    frames_count = min(frames_count, 32)
    total_size = file_info["Content-Length"]
    frame_size = round(total_size/frames_count)

    if verbose:
        print("Total file size", total_size)
        print("Each frame size", frame_size)

    frames_config = []
    byte_pos = 0
    for frame_i in range(frames_count):
        begin_byte_pos = frame_i * frame_size
        end_byte_pos = begin_byte_pos + frame_size - 1 if frame_i < frames_count-1 else total_size-1
        bytes_length = end_byte_pos - begin_byte_pos + 1
        frames_config.append({"frame_i": frame_i, "frame_name": "{}.part{}".format(filename, str(frame_i)), "range": "bytes={}-{}".format(str(begin_byte_pos), str(end_byte_pos)), "size": bytes_length})
    
    download_threads = []
    def download_frame_job(frame_config: dict):
        file_url = file_info["File-URL"]
        frame_file_name = frame_config["frame_name"]
        frame_file_index = frame_config["frame_i"]
        frame_range = frame_config["range"]

        req = requests.get(file_url, headers={"range": frame_range}, stream=True) # making streaming request for interation
        total_size = int(req.headers.get('Content-Length', 0)) # get total size in bytes
        block_size = 1024 #1 Kilobyte
        pb = tqdm(desc="Part {}".format(str(frame_file_index)), total=total_size, unit='B', unit_scale=True)
        
        with open(frame_file_name, 'wb') as f:
            for data in req.iter_content(block_size):
                pb.update(len(data))
                f.write(data)
        pb.close()
        if total_size != 0 and pb.n != total_size:
            print("ERROR, something went wrong")

    print("\n-> Downloading...", flush=True)
    download_begin_time = time.time()
    for frame_config in frames_config:
        new_thread = threading.Thread(target=download_frame_job, args=(frame_config,), daemon=True)
        download_threads.append(new_thread)
        new_thread.start()

    for download_thread in download_threads:
        download_thread.join() # wait all frame are downloaded
    downloaded_time = time.time() - download_begin_time
    print("Done {:.2f}s".format(downloaded_time))

    join_frames(filename, frames_count)

def get_file_md5(filename: str, uppercase: bool = True) -> str:
    """
    Get file MD5 checksum
    Params:
    ---
    filename (str): full file path
    Return:
    ---
    str: file MD5 
    """
    with open(filename, "rb") as f:
        file_hash = hashlib.md5()
        chunk = f.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(8192)

    return file_hash.hexdigest().upper() if uppercase else file_hash.hexdigest()