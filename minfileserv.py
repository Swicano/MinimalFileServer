# Write your code here :-)

import os
from adafruit_httpserver import status, exceptions
import html
import re
import io


def list_directory(path):
    """Helper to produce a directory listing (absent index.html).

    Return value is either a file object, or None (indicating an
    error).  In either case, the headers are sent, making the
    interface the same as for send_head().

    """
    try:
        list = os.listdir(path)
    except OSError:
        # self.send_error(
        #    exceptions.InvalidPathError,
        #    "No permission to list directory")
        return None
    list.sort(key=lambda a: a.lower())
    r = []
    try:
        displaypath = urllib_unquote(path, errors='surrogatepass')
    except UnicodeDecodeError:
        displaypath = urllib_unquote(path)
    displaypath = html.escape(displaypath, quote=False)
    enc = 'utf-8'  # sys.getfilesystemencoding()
    title = f'Directory listing for {displaypath}'
    r.append('<!DOCTYPE HTML>')
    r.append('<html lang="en">')
    r.append('<head>')
    r.append(f'<meta charset="{enc}">')
    r.append(f'<title>{title}</title>\n</head>')
    r.append(f'<body>\n<h1>{title}</h1>')
    r.append('<hr>\n<ul>')
    for name in list:
        fullname = ospath_join(path, name)
        displayname = linkname = name
        # Append / for directories or @ for symbolic links
        if ospath_isdir(fullname):
            displayname = name + "/"
            linkname = name + "/"
        if ospath_islink(fullname):
            displayname = name + "@"
            # Note: a link to a directory displays with @ and links with /
        r.append('<li><a href="%s">%s</a></li>'
                 % (urllib_quote(linkname, errors='surrogatepass'),
                    html.escape(displayname, quote=False)))
    r.append('</ul>\n<hr>\n</body>\n</html>\n')
    encoded = '\n'.join(r).encode(enc, 'surrogateescape')
    f = io.BytesIO()
    f.write(encoded)
    f.seek(0)
    # self.send_response(status.Status(200, 'OK'))
    # self.send_header("Content-type", "text/html; charset=%s" % enc)
    # self.send_header("Content-Length", str(len(encoded)))
    # self.end_headers()
    return f

# # #### URLLIB quote and unquote

def urllib_quote(string, safe='/', encoding=None, errors=None):
    """quote('abc def') -> 'abc%20def'

    Each part of a URL, e.g. the path info, the query, etc., has a
    different set of reserved characters that must be quoted. The
    quote function offers a cautious (not minimal) way to quote a
    string for most of these parts.

    RFC 3986 Uniform Resource Identifier (URI): Generic Syntax lists
    the following (un)reserved characters.

    unreserved    = ALPHA / DIGIT / "-" / "." / "_" / "~"
    reserved      = gen-delims / sub-delims
    gen-delims    = ":" / "/" / "?" / "#" / "[" / "]" / "@"
    sub-delims    = "!" / "$" / "&" / "'" / "(" / ")"
                  / "*" / "+" / "," / ";" / "="

    Each of the reserved characters is reserved in some component of a URL,
    but not necessarily in all of them.

    The quote function %-escapes all characters that are neither in the
    unreserved chars ("always safe") nor the additional chars set via the
    safe arg.

    The default for the safe arg is '/'. The character is reserved, but in
    typical usage the quote function is being called on a path where the
    existing slash characters are to be preserved.

    Python 3.7 updates from using RFC 2396 to RFC 3986 to quote URL strings.
    Now, "~" is included in the set of unreserved characters.

    string and safe may be either str or bytes objects. encoding and errors
    must not be specified if string is a bytes object.

    The optional encoding and errors parameters specify how to deal with
    non-ASCII characters, as accepted by the str.encode method.
    By default, encoding='utf-8' (characters are encoded with UTF-8), and
    errors='strict' (unsupported characters raise a UnicodeEncodeError).
    """
    if isinstance(string, str):
        if not string:
            return string
        if encoding is None:
            encoding = 'utf-8'
        if errors is None:
            errors = 'strict'
        string = string.encode(encoding, errors)
    else:
        if encoding is not None:
            raise TypeError("quote() doesn't support 'encoding' for bytes")
        if errors is not None:
            raise TypeError("quote() doesn't support 'errors' for bytes")
    return quote_from_bytes(string, safe)


_ALWAYS_SAFE = frozenset(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                         b'abcdefghijklmnopqrstuvwxyz'
                         b'0123456789'
                         b'_.-~')
_ALWAYS_SAFE_BYTES = bytes(_ALWAYS_SAFE)

def quote_from_bytes(bs, safe='/'):
    """Like quote(), but accepts a bytes object rather than a str, and does
    not perform string-to-bytes encoding.  It always returns an ASCII string.
    quote_from_bytes(b'abc def\x3f') -> 'abc%20def%3f'
    """
    if not isinstance(bs, (bytes, bytearray)):
        raise TypeError("quote_from_bytes() expected bytes")
    if not bs:
        return ''
    if isinstance(safe, str):
        # Normalize 'safe' by converting to bytes and removing non-ASCII chars
        safe = safe.encode('ascii', 'ignore')
    else:
        # List comprehensions are faster than generator expressions.
        safe = bytes([c for c in safe if c < 128])
    if not bs.rstrip(_ALWAYS_SAFE_BYTES + safe):
        return bs.decode()
    quoter = _byte_quoter_factory(safe)
    return ''.join([quoter(char) for char in bs])

# @functools.lru_cache
def _byte_quoter_factory(safe):
    return _Quoter(safe).__getitem__
    # that getitem might have to do with the functools.lru_cache

class _Quoter(dict):
    """A mapping from bytes numbers (in range(0,256)) to strings.

    String values are percent-encoded byte values, unless the key < 128, and
    in either of the specified safe set, or the always safe set.
    """
    # Keeps a cache internally, via __missing__, for efficiency (lookups
    # of cached keys don't call Python code at all).
    def __init__(self, safe):
        """safe: bytes object."""
        super().__init__()
        self.safe = _ALWAYS_SAFE.union(safe)
        self.inter = dict()
        self.inter[0] = chr(0) if 0 in self.safe else '%{:02X}'.format(0)

    def __repr__(self):
        return f"<Quoter {dict(self.inter)}>"

    # circuitpython doesnt use dunder_missing, override getitem to use get(x,default)
    # def __missing__(self, b):
    def __getitem__(self, b):
        try:
            # BEWARE circuitpython has a weird behaviour where if you override a
            #  function and inside call super().__getitem__ and the super() class
            #  calls self, it ends up executing the overriding function rather
            #  than the overridden one
            res = self.inter[b]
        except KeyError as exc:
            print(exc)
            # Handle a cache miss. Store quoted string in cache and return.
            res = chr(b) if b in self.safe else '%{:02X}'.format(b)
            self.inter[b] = res
        return res


_hexdig = '0123456789ABCDEFabcdef'
_hextobyte = None

def unquote_to_bytes(string):
    """unquote_to_bytes('abc%20def') -> b'abc def'."""
    # Note: strings are encoded as UTF-8. This is only an issue if it contains
    # unescaped non-ASCII characters, which URIs should not.
    if not string:
        # Is it a string-like object?
        string.split
        return b''
    if isinstance(string, str):
        string = string.encode('utf-8')
    bits = string.split(b'%')
    if len(bits) == 1:
        return string
    res = [bits[0]]
    append = res.append
    # Delay the initialization of the table to not waste memory
    # if the function is never called
    global _hextobyte
    if _hextobyte is None:
        _hextobyte = {(a + b).encode(): bytes.fromhex(a + b)
                      for a in _hexdig for b in _hexdig}
    for item in bits[1:]:
        try:
            append(_hextobyte[item[:2]])
            append(item[2:])
        except KeyError:
            append(b'%')
            append(item)
    return b''.join(res)

# _asciire = re.compile('([\x00-\x7f]+)')
# for some reason Cicruitpython re doesnt let me escape into hex like this
_asciire = re.compile('([\t-~]+)')  # this is equiv to '([\x0b-\x7e]+)'

def urllib_unquote(string, encoding='utf-8', errors='replace'):
    """Replace %xx escapes by their single-character equivalent. The optional
    encoding and errors parameters specify how to decode percent-encoded
    sequences into Unicode characters, as accepted by the bytes.decode()
    method.
    By default, percent-encoded sequences are decoded with UTF-8, and invalid
    sequences are replaced by a placeholder character.

    unquote('abc%20def') -> 'abc def'.
    """
    if isinstance(string, bytes):
        return unquote_to_bytes(string).decode(encoding, errors)
    if '%' not in string:
        string.split
        return string
    if encoding is None:
        encoding = 'utf-8'
    if errors is None:
        errors = 'replace'
    bits = _asciire.split(string)
    res = [bits[0]]
    append = res.append
    for i in range(1, len(bits), 2):
        append(unquote_to_bytes(bits[i]).decode(encoding, errors))
        append(bits[i + 1])
    return ''.join(res)


# ########## Need to Fake some os.path functionality

def ospath_join(patha, pathb):
    # os.path.join has some odd behaviour
    if patha[-1] in (os.sep, '\\', '/'):
        return patha+pathb
    else:
        return patha+os.sep+pathb

def ospath_isdir(path):
    return os.stat(path)[0] == 0x4000

def ospath_isfile(path):
    return os.stat(path)[0] == 0x8000

def ospath_islink(path):
    # the microsd card im using doesnt support symlinks anyway,
    # so noway to test what the magic number should be
    return False

