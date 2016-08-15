#!/usr/bin/env python	

import requests
import os
import shutil
from git import Repo
import config
import json
import argparse
import sys


class Gitlab(object):


    def __init__(self, server_url, token):
        self.server_url = server_url
        self.base_url = server_url + '/api/v3'  
        self.token = token
        self.headers = {'Content-type': 'application/json', 'PRIVATE-TOKEN': self.token}

    def fetch_users(self, page_size):

        payload = { 'per_page': page_size}

        users_url = self.base_url + '/users'

        r = requests.get(users_url, headers = self.headers, params = payload)
        
        return r.json();

    def fetch_groups(self, page_size):

        payload = { 'per_page': page_size}

        groups_url = self.base_url + '/groups'

        r = requests.get(groups_url, headers = self.headers, params = payload)
        
        return r.json();

    def fetch_group_members(self, id):

        groups_url = self.base_url + '/groups/' + str(id) + '/members'

        r = requests.get(groups_url, headers = self.headers)
        
        return r.json();        

    def add_group_members(self, id, user_id, access_level):

        payload = { 'user_id': user_id, 'access_level': access_level}

        groups_url = self.base_url + '/groups/' + str(id) + '/members'

        r = requests.post(groups_url, headers = self.headers, params = payload)
        
        return r.json();        



    def fetch_namaespaces(self, page_size):

        payload = { 'per_page': page_size}

        namespace_url = self.base_url + '/namespaces'

        r = requests.get(namespace_url, headers = self.headers, params = payload)
        
        return r.json();

    def fetch_project_members(self, id):

        members_url = self.base_url + '/projects/' + str(id) + '/members'

        r = requests.get(members_url, headers = self.headers)
        
        return r.json();        

    def namespace_lookup(self, name):

        payload = {'search': name}

        namespace_url = self.base_url + '/namespaces'

        r = requests.get(namespace_url, headers = self.headers, params = payload)
                
        return r.json();        

    def fetch_all_projects(self, page_size):

        payload = { 'per_page': page_size}

        projects_url = self.base_url + '/projects/all'

        r = requests.get(projects_url, headers = self.headers, params = payload)
               
        return r.json();


    def search_project(self, name, page_size):

        payload = { 'per_page': page_size}

        projects_url = self.base_url + '/projects/search/' + name

        print 'Searching ', projects_url

        r = requests.get(projects_url, headers = self.headers, params = payload)
               
        return r.json();        


    def create_users(self, users):

        users_url = self.base_url + '/users'

        for user in users: 
            print 'creating user -> ', user['name']
            user['password'] = config.settings['default_password']
            r = requests.post(users_url, headers = self.headers, params = user)        
            if r.status_code == 201:
                print 'User created successfully'
            else:    
                print r.json()['message']



    def create_groups(self, groups, users, gitlab_ref):

        groups_url = self.base_url + '/groups'

        for grp in groups: 

            print 'Creating group -> ', grp['name']

            r = requests.post(groups_url, headers = self.headers, params = grp) 

            if r.status_code == 201:
                print 'Group created successfully'
                
                new_grp_id = r.json()['id']
                group_members = gitlab_ref.fetch_group_members(grp['id'])

                for user in users:
                    for member in group_members:                
                        if user['username'] == member['username']:
                            self.add_group_members(new_grp_id, member['access_level'], user['id'])
                            print '\tGroup member ' + user['username'] + ' added'

            else:    
                print r.json()['message']


    def add_project_member(self, proj_id, access_level, user_id):
        
        payload = {'user_id': user_id, 'access_level': access_level }

        projects_url = self.base_url + '/projects/' + str(proj_id) + '/members'

        r = requests.post(projects_url, headers = self.headers, params = payload)
           
        if r.status_code == 201:
            print 'Project member added successfully'
        else:    
            print 'Failed to add project member'
        

    def create_projects(self, old_users, projects, gitlab_ref):
        
        total_users    = config.settings['total_users']
        new_users = self.fetch_users(total_users);

        for prj in projects: 
            print 'creating project -> ', prj['path_with_namespace']

            namespace = self.namespace_lookup(prj['namespace']['name'])

            prj_id = prj['id']
            project_members = gitlab_ref.fetch_project_members(prj_id)



            if namespace[0]['kind'] == 'group':                        
                project_url = self.base_url + '/projects'

                project = {}
                project['name'] = prj['name']
                project['path'] = prj['path']
                project['namespace_id'] = namespace[0]['id']
                project['description'] = prj['description']
                project['issues_enabled'] = prj['issues_enabled']
                project['merge_requests_enabled'] = prj['merge_requests_enabled']            
                project['wiki_enabled'] = prj['wiki_enabled']
                project['snippets_enabled'] = prj['snippets_enabled']            
                project['public'] = prj['public']
                project['visibility_level'] = prj['visibility_level']

            else:
                creator_id = prj['creator_id']
                old_user = [usr for usr in old_users 
                            if usr['id'] == creator_id]
            
                new_user = [usr for usr in new_users
                            if usr['username'] == old_user[0]['username']]

                new_user_id = new_user[0]['id']

                project_url = self.base_url + '/projects/user/' + str(new_user_id)

                project = {}
                project['name'] = prj['name']
                project['path'] = prj['path']                
                project['description'] = prj['description']
                project['issues_enabled'] = prj['issues_enabled']
                project['merge_requests_enabled'] = prj['merge_requests_enabled']            
                project['wiki_enabled'] = prj['wiki_enabled']
                project['snippets_enabled'] = prj['snippets_enabled']            
                project['public'] = prj['public']
                project['visibility_level'] = prj['visibility_level']


            r = requests.post(project_url, headers = self.headers, params = project)        
            if r.status_code == 201:
                print 'Project created successfully'

                new_prj_id = r.json()['id']

                for user in new_users:
                    print '\tAdding project member: ' + user + 'to project '+ project['name']
                    for member in project_members:                
                        if user['username'] == member['username']:
                            self.add_project_member(new_prj_id, member['access_level'], user['id'])
                            print '\tProject member ' + member['username'] + ' added to project'
            else:    
                print r.json()


    def mirror_repos(self, g1projects, total):

        g2projects = self.fetch_all_projects(total)

        for prj in g1projects: 

            path_with_namespace = prj['path_with_namespace']

            print 'Mirroring project -> ', path_with_namespace

            if not prj['default_branch']:
                print 'Empty repository, skipping'
                continue
            
            repo_url = prj['ssh_url_to_repo']
            clone_dir = prj['path']

            working_dir = config.settings['working_dir']

            repo_dir = working_dir + path_with_namespace

            if os.path.exists(repo_dir):
                print 'Mirror project ' + path_with_namespace + ' completed'
                continue

            os.makedirs(repo_dir)

            args = { 'mirror' : True }

            Repo.clone_from(repo_url, repo_dir, progress=None, env=None,  **args)

            g2prj = [m_prj for m_prj in g2projects 
                            if m_prj['path_with_namespace'] == path_with_namespace]
            
            new_repo_url = g2prj[0]['ssh_url_to_repo']
            
            repo = Repo(repo_dir)
            git = repo.git

            git.push('--mirror', new_repo_url)

            clean_up = config.settings['clean_up'] 
            if clean_up:
                print 'Cleaning up working directory -> ', working_dir
                shutil.rmtree(working_dir)

            print 'Mirroring project ' + path_with_namespace + ' completed successfully'

    
    def migrate_to(self, gitlab2):

        total_groups   = config.settings['total_groups']
        total_users    = config.settings['total_users']
        total_projects = config.settings['total_projects']

        groups   = self.fetch_groups(total_groups)
        
        users    = self.fetch_users(total_users)    

        projects = self.fetch_all_projects(total_projects)
     

        print
        print 'Migrating users, please wait...'
        gitlab2.create_users(users)

        print
        print 'Migrating groups, please wait...'
        gitlab2.create_groups(groups, users, self)

        print
        print 'Migrating projects, please wait...'
        gitlab2.create_projects(users, projects, self)

        print
        print 'Migrating project repositories, please wait...'
        # gitlab2.mirror_repos(projects, total_projects)
   

def main():

    print
    print 'Migrating Gitlab, please wait...'
    print

    gitlab1_server = config.settings['gitlab1']['server']  
    gitlab1_token  = config.settings['gitlab1']['access_token']  

    gitlab2_server = config.settings['gitlab2']['server']  
    gitlab2_token  = config.settings['gitlab2']['access_token']  

    gitlab1 = Gitlab(gitlab1_server, gitlab1_token)
    gitlab2 = Gitlab(gitlab2_server, gitlab2_token)  

    gitlab1.migrate_to(gitlab2)

    
    print
    print 'Migration completed successfully'
    print


if __name__ == '__main__':
   main()