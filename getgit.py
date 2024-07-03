#!/usr/bin/env python
import requests
import argparse
import os
import re
import pathlib
import concurrent.futures

def git_checkout(full_local_path,ssh_url):
    if os.path.isdir(full_local_path) == True:
        if os.path.isdir(full_local_path + "/.git") == False:
            # The directory exists but there's no .git subdir, so remove it
            os.rmdir(full_local_path)

    if os.path.isdir(full_local_path) == False:
        # Need to check it out
        local_path_only = os.path.dirname(full_local_path)
        pathlib.Path(local_path_only).mkdir(parents=True, exist_ok=True)
        os.chdir(local_path_only)
        os.system("git clone --quiet --recursive " + ssh_url + " " + full_local_path)
        print("Cloned: " + ssh_url + " [" + full_local_path + "]")
    else:
        # Need to pull
        os.chdir(full_local_path)
        os.system("git pull --quiet")
        print("Pulled: " + full_local_path)

def get_project_list(current_page,args):
    base_uri = args['base_uri']
    local_dir = args['local_directory']
    all_projects_headers = {
        "PRIVATE-TOKEN":args['token'],
        }

    results_per_page = args['results_per_page']
    all_projects_uri = base_uri + "/api/v4/projects?page=" + str(current_page) + "&per_page=" + str(results_per_page)
    r = requests.get(all_projects_uri, headers=all_projects_headers)
    
    if r.status_code==200:
        total_pages = int(r.headers['X-Total-Pages'])
        next_page = int(r.headers['X-Next-Page'])
        current_page = int(r.headers['X-Page'])
    
        print("*** Pool start")
        pool = concurrent.futures.ThreadPoolExecutor(max_workers=args['number_of_processes'])

        for project in r.json():
            ssh_url = project['ssh_url_to_repo']
            path_with_namespace = project['path_with_namespace']
            project_id = project['id']
            full_local_path = local_dir + '/' + path_with_namespace
    
            # Checkout the main path
            pool.submit(git_checkout, full_local_path, ssh_url)
    
            has_wiki_url = base_uri + "/api/v4/projects/" + str(project_id) + "/wikis"
            w = requests.get(has_wiki_url, headers=all_projects_headers)
            if w.status_code==200:
                if len(w.json()) > 0:
                    path_with_namespace = path_with_namespace + ".wiki"
                    full_local_path = local_dir + '/' + path_with_namespace
                    ssh_wiki_url = re.sub('\.git$', '.wiki.git', ssh_url)
                    pool.submit(git_checkout,full_local_path, ssh_wiki_url)

        pool.shutdown(wait=True)
        print("*** Pool finished")

        # If there's another page, visit it
        if (next_page > 0) and (next_page > current_page) and (next_page <= total_pages):
            get_project_list(next_page,args)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Checkout and pull an entire organisation\'s gitlab repo (including wikis).')
    parser.add_argument('-p', '--results-per-page', type=int, action='store', required=False, default=100, help='How many results per page to request (default: 100)')
    parser.add_argument('-t', '--token', action='store', required=True, help='The gitlab API token to use')
    parser.add_argument('-u', '--base-uri', action='store', required=True, help='The base URI to use (e.g. https://git.boat.internal)')
    parser.add_argument('-d', '--local-directory', action='store', required=True, help='The directory to use as a base (no trailing slash, e.g. /home/mast/git-boat-repo)')
    parser.add_argument('-n', '--number-of-processes', type=int, action='store', default=25, required=False, help='Number of parallel checkout processes (default: 25)')
    args = vars(parser.parse_args())
    current_page = 1
    get_project_list(current_page,args)

