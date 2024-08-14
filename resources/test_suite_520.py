#!/usr/bin/python3

import pathlib
import argparse
import shutil
import subprocess
import sys
import re
import os
import git

import repo_test
from repo_test_suite import repo_test_suite

class test_suite_520(repo_test_suite):

    def __init__(self, repo, assignment_name, min_err_commits = 3, max_repo_files = 20):
        # Reference to the Git repository
        super().__init__(repo,test_name = assignment_name)
        self.repo_tests = []
        self.build_tests = []
        self.clean_tests = []
        self.add_repo_tests(min_err_commits,max_repo_files)
        self.add_clean_tests()
        self.run_repo_tests = True
        self.run_build_tests = True
        self.run_clean_tests = True

    def add_repo_tests(self, min_err_commits, max_repo_files):
        self.add_repo_test(repo_test.list_git_commits())
        self.add_repo_test(get_err_git_commits(min_err_commits))
        self.add_repo_test(repo_test.check_for_uncommitted_files())
        self.add_repo_test(repo_test.check_for_max_repo_files(max_repo_files))

    def add_clean_tests(self):
        self.add_clean_test(repo_test.check_for_untracked_files())
        self.add_clean_test(repo_test.make_test("clean"))
        self.add_clean_test(repo_test.check_for_ignored_files())

    def add_repo_test(self,test):
        self.repo_tests.append(test)

    def add_clean_test(self,test):
        self.clean_tests.append(test)

    def add_build_test(self,test):
        self.build_tests.append(test)

    def add_make_test(self,make_rule):
        make_test = repo_test.make_test(make_rule)
        self.add_build_test(make_test)

    #def run_tests(self, run_repo_tests = True, run_build_tests = True, run_clean_tests = True):
    def run_tests(self):
        ''' Run all the registered tests '''
        self.print_test_start_message()
        test_num = 1
        if self.run_repo_tests:
            self.iterate_through_tests(self.repo_tests, start_step = test_num)
            test_num += len(self.repo_tests) 
        if self.run_build_tests:
            self.iterate_through_tests(self.build_tests, start_step = test_num)
            test_num += len(self.build_tests) 
        if self.run_clean_tests:
            self.iterate_through_tests(self.clean_tests, start_step = test_num)
            test_num += len(self.clean_tests) 
        self.print_test_end_message()

def build_test_suite_520(assignment_name,  min_err_commits = 3, max_repo_files = 20):
    parser = argparse.ArgumentParser(description=f"Test suite for 520 Assignment: {assignment_name}")
    parser.add_argument("--repo", help="Path to the repository to test (default is current directory)")
    parser.add_argument("--norepo", action="store_true", help="Do not run Repo tests")
    parser.add_argument("--nobuild", action="store_true", help="Do not run build tests")
    parser.add_argument("--noclean", action="store_true", help="Do not run clean tests")
    #parser.add_argument("--min_err_commits", type=int, default=3, help="Minimum number of error commits")
    #parser.add_argument("--max_repo_files", type=int, default=20, help="Maximum number of files in the repository")
    args=parser.parse_args()
    if args.repo is None:
        path = os.getcwd()
    else:
        path = args.repo
    repo = git.Repo(path, search_parent_directories=True)
    test_suite = test_suite_520(repo, assignment_name, min_err_commits = min_err_commits, max_repo_files = max_repo_files)
    if args.norepo:
        test_suite.run_repo_tests = False
    if args.nobuild:
        test_suite.run_build_tests = False
    if args.noclean:
        test_suite.run_clean_tests = False
    return test_suite

class get_err_git_commits(repo_test.repo_test):
    ''' Prints the commits of the given directory in the repo.
    '''
    def __init__(self, min_msgs, check_path = None, check_str = "ERR"):
        '''  '''
        super().__init__()
        self.check_path = check_path
        self.min_msgs = min_msgs
        self.check_str = check_str

    def module_name(self):
        return "Check for minimum number of error commits"

    def perform_test(self, repo_test_suite):
        if self.check_path is None:
            self.check_path = repo_test_suite.working_path

        relative_path = self.check_path.relative_to(repo_test_suite.repo_root_path)
        repo_test_suite.print(f'Checking for ERR commits in {relative_path}')
        commits = list(repo_test_suite.repo.iter_commits(paths=relative_path))
        chk_commits = []
        for commit in commits:
            commit_message = commit.message.strip()
            if self.check_str in commit_message:
                chk_commits.append(commit_message)
                print(commit_message)
        if len(chk_commits) >= self.min_msgs:
            return True
        else:
            repo_test_suite.print_error(f"Insufficient number of error commits: found {len(chk_commits)} but expecting {self.min_msgs}")
            return False