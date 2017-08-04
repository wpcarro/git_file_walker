#!/usr/local/bin/python3

import os
import sys
import git
import colorama
import subprocess
import argparse


def browse_file_history(repo_dir, filename, **kwargs):
    should_reverse = kwargs['rev']
    count = kwargs['count']

    g = git.Git(repo_dir)
    commits = file_commits(g, filename)

    if should_reverse:
        commits.reverse()
        commits = commits[:count]
    else:
        commits = commits[:count]

    pages = (trim_and_colorize_diff(g.show(commit, filename)) for commit in commits)

    pages = (trim_and_colorize_diff(g.show(commit, filename)) for commit in commits)
    clear_screen()

    for page in pages:
        page_output(page)
        clear_screen()


def clear_screen():
    # LIMITATION: need to run 'cls' on Windows
    os.system('clear')


def page_output(page):
    try:
        pager = subprocess.Popen(['less', '-R', '-S', '-X', '-K'], stdin=subprocess.PIPE, stdout=sys.stdout)
        for line in page:
            pager.stdin.write(bytearray(line, 'utf8'))
        pager.stdin.close()
        pager.wait()
    except KeyboardInterrupt:
        # defer to `less`
        pass


def trim_and_colorize_diff(content):
    seen_at_at = False
    colorized = []

    for line in content.split('\n'):
        if seen_at_at:
            if line.startswith('+'):
                colorized.append(colorama.Fore.GREEN + line + colorama.Style.RESET_ALL)
            elif line.startswith('-'):
                colorized.append(colorama.Fore.RED + line + colorama.Style.RESET_ALL)
            else:
                colorized.append(line)
        else:
            if line.startswith('@@'):
                seen_at_at = True

    return '\n'.join(colorized)


def file_commits(g, filename):
    return g.log('--pretty=%H','--follow','--',filename).split('\n')


if __name__ == '__main__':
    # Parse CLI args
    parser = argparse.ArgumentParser(description='Step through a file\'s git history.')
    parser.add_argument('filename', metavar='file', type=str, nargs=1, help='path of the file to browse')
    parser.add_argument('-r', '--rev', dest='reverse', action='store_true', help='browse the history in reverse (default: False)')
    parser.add_argument('-c', '--count', dest='count', type=int, default=20, help='maximum number of commits to view (default: 20)')
    args = parser.parse_args()

    # Initialize colorama for Windows platform
    colorama.init()

    # LIMITATION: can only run this program successfully from the repo's root
    repo_dir = os.getcwd()

    filename = args.filename
    browse_file_history(repo_dir, filename, rev=args.reverse, count=args.count)


