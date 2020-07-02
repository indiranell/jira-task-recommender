from jira import JIRA
import datetime
import conf

username = conf.username
apitoken = conf.apitoken
server = conf.server

class LocalJira(JIRA):
    def __init__(self,server,username,apitoken):
        super().__init__(server=server,basic_auth=(username,apitoken))

    def get_projects(self):
        "Get the projects"
        
        return self.projects()

    def get_issues(project_id):
        "Get the Issues"
        issues = jira.search_issues(project_id)

        return issues

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

        time_difference = datetime.datetime.fromisoformat(time_spent['done']) - datetime.datetime.fromisoformat(time_spent['doing'])

        return time_difference

    def get_projects_using_keyword(self,keyword):
        "Get the projects that has the given keyword"
        req_projects = []
        projects = self.get_projects()
        for project in projects:
            if keyword.lower() in project.name.lower():
                req_projects.append(project)
        
        return req_projects

if __name__ == '__main__':
    obj = LocalJira(server,username,apitoken)
    print(obj.get_projects_using_keyword('onboarding'))



