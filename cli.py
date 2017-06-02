#!/usr/bin/env python


# $Id$


import sys
import os
import optparse

import compare
import walk


PROGRAM_VERSION = '0.1'


# Choices for the --follow-symlinks command-line option. The order of the
# choices is important (it's used for -P, -L and in the help strings).
_SYMLINK_CHOICES = ('never', 'always', 'directory', 'file')



def parse_args():
    """Parse the command-line arguments.

    Returns the tuple (options, base_image, compare_list).

    """
    cmdline_usage = '%prog [options] BASE_IMAGE IMAGE...'

    cmdline_version = '%%prog %s' % PROGRAM_VERSION

    prog_name = os.path.basename(sys.argv[0])

    parser = optparse.OptionParser(usage=cmdline_usage,
                                           version=cmdline_version)

    parser.add_option('-L', '--dereference', action='store_const',
                      const=_SYMLINK_CHOICES[1], dest='follow_symlinks',
                      help='follow all symbolic links (enabled by default)')

    parser.add_option('-P', '--no-dereference', action='store_const',
                      const=_SYMLINK_CHOICES[0], dest='follow_symlinks',
                      help='never follow any symbolic links')

    parser.add_option('-R', '-r', '--recursive', action='store_true',
                      dest='recursive', default=False,
                      help='recurse into directories')

    parser.add_option('--follow-symlinks', action='store', metavar='when',
                      choices=_SYMLINK_CHOICES, dest='follow_symlinks',
                      default=_SYMLINK_CHOICES[1],
                      help="when to follow symlinks: '%s' (same as -P), '%s' "
                      "(default, same as -L), '%s' (only when pointing to a "
                      "directory), '%s' (only when pointing to a file)"
                        % _SYMLINK_CHOICES)

    (cmdline_opts, cmdline_args) = parser.parse_args()

    # make sure we're given the base image for comparison
    if len(cmdline_args) < 1:
        parser.error("missing base image argument\n"
                     "Try `%s --help' for more information." % prog_name)

    # make sure we have at least one image to compare against
    if len(cmdline_args) < 2:
        parser.error("must specify at least one image to compare with the base\n"
                     "Try `%s --help' for more information." % prog_name)


    return cmdline_opts, cmdline_args[0], cmdline_args[1:]



if __name__ == '__main__':
    options, base_image, compare_list = parse_args() 

    # TODO: Finish implementing.
