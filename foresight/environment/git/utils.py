import os, logging

logger = logging.getLogger(__name__)

# Platform independently user home folder path.
user_home_dir = os.path.expanduser("~")


def get_parent_dir(path):
    return os.path.abspath(os.path.join(path, os.pardir))


def backward_search_for_file(starting_path, filename_to_search):
    try:
        if starting_path and filename_to_search and starting_path != user_home_dir:
            current_folder_items = os.listdir(starting_path)
            if filename_to_search in current_folder_items:
                return starting_path
            starting_path = get_parent_dir(starting_path)
            return backward_search_for_file(starting_path, filename_to_search)
    except Exception as e:
        logger.error("backward_search_for_file error: {}".format(e))
        pass
    return None