from jira import JIRA
import datetime
import pickle
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

    def get_issues(self,project_id):
        "Get the Issues"
        issues = self.search_issues("project='%s'"%project_id)

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


if __name__ == '__main__':
    obj = LocalJira(server,username,apitoken)
    projects = obj.get_projects_using_keyword('onboading')
    issues = {}
    for project in projects:
        issues['%s'%project.key] = obj.get_issues(project)
        issues_list = []
        for issue in issues['%s'%project.key]:
            time_diff = obj.get_time_spent(issue.id)
            issues_list.append({issue.raw['fields']['summary'] : time_diff})
        issues['%s'%project.key] = issues_list
            #print(issue.raw['fields']['summary'],time_diff)
        #issues['%s'%project.key].add(issue.raw['fields']['summary'],time_diff)
    print(issues)


