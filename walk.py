
# $Id$

import os
import sys



def _print_error(error):
    """Print a listing error to stderr.

    error should be an os.OSError instance.

    """

    sys.stderr.write("error listing '%s': %s\n"
                     % (error.filename, error.strerror))



def _raise(error):
    """Raise an exception.

    This is only a function to wrap the raise keyword, so we can use it in
    places where a function is required.

    """
    raise error



_error_handlers = {
    'abort': _raise,
    'ignore': None,
    'print': _print_error,
}



# TODO: Implement Python >=2.6 version of walk, using os.walk's followlinks
# argument. Make walk an alias for either walk25 or walk26 at import time,
# depending on sys.version_info.


# XXX: Symlinks pointing to parent directories can lead to infinite loops.
# We're not detecting that here. May want to keep track of the directories
# we've visited so we can deal with it. Python 2.6's walk with
# followlinks=True also doesn't detect infinite loops, so we'd have to use
# it with followlinks=False as with walk25 and implement our own logic.



def walk(top_dir, follow_links=False, on_error='print'):
    """Directory tree generator.

    For each directory in the directory tree rooted at top_dir (including
    top_dir itselfl, but excluding '.' and '..'), yields a 3-tuple

        dirpath, subdirs, filenames

    See the help for os.walk for further details. follow_links, if true,
    specifies that symbolic links to directories should be followed. Note
    that no verification is done for infinite link loops (e.g. a symlink
    pointing to a parent directory).
    
    on_error specifies what to do in case of error while trying to list a
    given directory. It can be a function, which will be called with an
    os.error instance as its single argument, or it can be one of 'abort',
    'ignore', or 'print' for predefined behavior. Respectively, 'abort'
    will raise an OSError exception, 'ignore' will ignore the error and
    continue, and 'print' will print an error to sys.stderr and continue.

    This is basically a wrapper for os.walk() that always has the
    follow_links option (instead of only for Python >=2.6), and with
    optional predefined behavior on error.

    """
    if callable(on_error):
        error_handler = on_error
    else:
        error_handler = _error_handlers[on_error]

    for dirpath, subdirs, filenames in os.walk(top_dir, onerror=error_handler):
        for filename in filenames:
            full_filename = os.path.join(dirpath, filename)

            # check if the file is a symlink to a directory
            if (follow_links and os.path.islink(full_filename)
                    and os.path.isdir(full_filename)):
                # add the symlink to the list of directories to crawl
                subdirs.append(filename)

        yield dirpath, subdirs, filenames
