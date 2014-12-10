#!/usr/bin/env python
"""
Check on Galera.
Report the seqno or server status.
"""


from __future__ import print_function
import sys
import psutil
import ConfigParser
import io

DEBUG = True


def debug_print(string):
    """Print a string to stdout when DEBUG is set to True."""
    if DEBUG:
        print("DEBUG: " + string)


def error_print(string):
    """Print a string to stderr."""
    print("ERROR: " + string, file=sys.stderr)


def is_boostrap_process_running(pid_list):
    """
    Check whether the mysql init script is running with the
    --wsrep-new-cluster option. Return a boolean.

    """
    return ['/bin/sh', '/etc/init.d/mysql', 'start',
            '--wsrep-new-cluster'] in [psutil.Process(pid).cmdline for
                                       pid in pid_list]


def is_mysqld_process_running(pid_list):
    """Check whether the mysqld process is running. Return a boolean."""
    return "mysqld" in [psutil.Process(pid).name for pid in pid_list]


def is_galera_init_process_running(pid_list):
    """Check whether the galera_init process is running. Return a boolean."""
    return "galera_init" in [psutil.Process(pid).name for pid in pid_list]


def status():
    """
    Print a word describing the status of mysqld or the initiator script.

    """
    # Get a list of all currently running processes.
    pid_list = psutil.get_pid_list()
    # Check if one of them looks like a bootstrap process.
    if is_boostrap_process_running(pid_list):
        print("bootstrapping")
        sys.exit(0)
    # Check if one of them looks like a mysqld process.
    if is_mysqld_process_running(pid_list):
        print("running")
        sys.exit(0)
    # Check if one of them looks like a galera_init process.
    if is_galera_init_process_running(pid_list):
        print("initiating")
        sys.exit(0)
    # If none of the above is true, the status is simply stopped.
    print("stopped")
    sys.exit(0)


def seqno():
    """Print the log position of the database."""
    grastate_file_path = "/var/lib/mysql/grastate.dat"
    try:
        grastate_file = open(grastate_file_path)
    except IOError:
        print(-1)
        sys.exit(0)
    # The grastate.dat file is technically not valid ini, because it doesn't
    # have a header. Prepend a header so ConfigParser doesn't notice.
    # http://stackoverflow.com/questions/2819696/
    grastate_ini = u'[grastate]\n'+''.join([x for x in grastate_file])
    config = ConfigParser.RawConfigParser()
    config.readfp(io.StringIO(grastate_ini))
    # Look up and print the seqno.
    print(config.get("grastate", "seqno"))
    grastate_file.close()
    sys.exit(0)


def main(argv):
    """The main function."""
    if len(argv) > 1:
        if argv[1] == 'status':
            status()
            sys.exit(0)
        if argv[1] == 'seqno':
            seqno()
            sys.exit(0)
    error_print("Please run this command with either the 'status' or "
                + "'seqno' argument.")
    sys.exit(1)

if __name__ == "__main__":
    main(sys.argv)
