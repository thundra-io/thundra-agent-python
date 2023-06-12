
def bytes_to_str(value):
    """Convert byte to string

    Args:
        value (byte]):  

    Returns:
        [str]: value if value is str o.w str(value)
    """
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value


def extract_headers(connection_obj):
    """Convert nested list headers in request/response object to dict

    Args:
        connection_obj (obj): request or response object

    Returns:
        dict: request or response headers dict version
    """
    headers = connection_obj.get("headers")
    if headers:
        return dict((bytes_to_str(k), bytes_to_str(v)) for (k,v) in headers)
    return {}