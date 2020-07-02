from jira import JIRA
import datetime
import pickle
import os
import pandas as pd
import conf

username = conf.username
apitoken = conf.apitoken
server = conf.server

class LocalJira(JIRA):
    "Local Jira object"

    def __init__(self,server,username,apitoken):
        super().__init__(server=server,basic_auth=(username,apitoken))

    def get_projects(self):
        "Get the projects"
        
        return self.projects()

    def get_issues(self,project_id):
        "Get the Issues"
        issues = self.search_issues("project='%s'"%project_id)

        return issues
    
    def get_issues_from_projects(self,projects_list):
        "Get the issue from a project list"
        issues_list = []
        for project in projects:
            all_project_issues = self.get_issues(project)
            for issue in all_project_issues:
                time_diff = self.get_time_spent(issue.id)
                issues_list.append((issue.id,issue.raw['fields']['summary'],time_diff))
        return issues_list

    def get_time_spent(self,issue_id):
        "Get the time spent on each issue"
        issue = self.issue(issue_id, expand='changelog')
        time_spent = {}
        changelog = issue.changelog
        for history in changelog.histories:
            for item in history.items:
                if item.field == 'status':
                    if(item.toString == 'In Progress'):
                        time_spent['doing'] = history.created.split('+')[0]
                    elif(item.toString == 'Done'):
                        time_spent['done'] = history.created.split('+')[0]
        if(time_spent.get('done') and time_spent.get('doing')):
            time_difference = datetime.datetime.fromisoformat(time_spent['done']) - datetime.datetime.fromisoformat(time_spent['doing'])

            return time_difference.days * 8

    def get_projects_using_keyword(self,keyword):
        "Get the projects that has the given keyword"
        req_projects = []
        projects = self.get_projects()
        for project in projects:
            if keyword.lower() in project.name.lower():
                req_projects.append(project)

        return req_projects

    def pickle_data(self,data_obj,filename):
        "Pickle the data"
        with open(filename,'ab') as pf:
            pickle.dump(data_obj,pf)

if __name__ == '__main__':
    obj = LocalJira(server,username,apitoken)
    #obj.get_projects()
    if not os.path.exists('issues'):
        projects = obj.get_projects_using_keyword('onboarding')
        issues_list = obj.get_issues_from_projects(projects)
        print(issues_list)
        obj.pickle_data(issues_list,'issues')
    with open('issues','rb') as pf:
        issues = pickle.load(pf)
    issues_df = pd.DataFrame(issues, columns = ['issue_id','summary','time_taken'])
    pd.set_option('display.max_rows', None)
    #print(issues_df)
    #print(dir(issues_df))
    print(issues_df[issues_df['summary'] == 'Create an html page for your test strategy report'])
    print(issues_df.groupby(['summary']).mean())
    #print(issues_df[issues_df.duplicated(['summary'])])


