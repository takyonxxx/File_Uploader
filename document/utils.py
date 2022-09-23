import json
import os
import re
from configparser import ConfigParser

from connection.file_uploader import FileUploader

config = ConfigParser()


def read_configuration(delimiter='='):
    if os.path.isfile("config.ini"):
        config.read("config.ini")
        exclude_extensions = config.get('default', 'exclude_extensions', raw=True, fallback="[.wav, .mp3, .mp4]")
        max_file_size = config.getint('default', 'max_file_size', raw=True, fallback=16777216)

        return exclude_extensions, max_file_size
    else:
        print(f"Config file[config.ini] is not found.")
        return None


def validate_regex_pattern(pattern):
    pattern = r"{}".format(pattern)
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False


def get_dict_coumt(d):
    cnt = 0
    for e in d:
        if type(d[e]) is dict:
            cnt += get_dict_coumt(d[e])
    else:
        cnt += 1
    return cnt


def format_str(word):
    try:
        if isinstance(word, bytes):  # Check if it's in bytes
            return word.decode('utf-8').replace("\r\n", "")
        elif isinstance(word, str):
            return word.replace("\r\n", "")
        elif isinstance(word, dict):
            return json.dumps(word)
        else:
            return None
    except Exception as e:
        print("format_str error : {}".format(e))


def clean_string(text):
    text = format_str(text)
    if text:
        special_char_list = ['$', '#', '&', '%', 'é', '"', '!', '\\', '£', '^', '+', '½']
        text = "".join([k for k in text if k not in special_char_list])
        text = "".join([s for s in text.strip().splitlines(True) if s.strip("\r\n").strip()])
    return text


def get_file_uploader():
    file_uploader = FileUploader.get_instance()
    if file_uploader:
        return file_uploader
    else:
        return None
