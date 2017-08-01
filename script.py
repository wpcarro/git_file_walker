#!/usr/local/bin/python3

import os
import sys
import git
import colorama
import subprocess


def browse_file_history(repo_dir, filename):
    g = git.Git(repo_dir)
    commits = file_commits(g, filename)
    pages = (trim_and_colorize_diff(g.show(commit, filename)) for commit in reversed(commits))
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
    # Initialize colorama for Windows platform
    colorama.init()

    # LIMITATION: can only run this program successfully from the repo's root
    repo_dir = os.getcwd()

    filename = sys.argv[1]
    browse_file_history(repo_dir, filename)


