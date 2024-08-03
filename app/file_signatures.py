"""
File signature identitication
"""


def guess_mime_type(data: bytes) -> str:
    """Guess the MIME type based on a few known signatures

    Parameters
    ----------
    data : bytes
        Original data of the file

    Returns
    -------
    str
        Guessed MIME type
    """
    if data.startswith(b'\xff\xd8\xff'):
        return 'image/jpeg'
    if data.startswith(b'\x89\x50\x4e\x47'):
        return 'image/png'
    if data.startswith(b'\x00\x00\x00\x0c\x6a\x50'):
        return 'image/jp2'
    if data.startswith(b'GIF8'):
        return 'image/gif'
    if data.startswith(b'RIFF') and (data[8:12] == b'WEBP'):
        return 'image/webp'

    return 'application/octet-stream'
