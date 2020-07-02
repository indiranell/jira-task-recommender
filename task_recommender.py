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
        return self.projects()

    def get_issues(project_id):
        issues = jira.search_issues(project_id)
        return issues

    def get_time_spent(self,issue_id):
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

if __name__ == '__main__':
    obj = LocalJira(server,username,apitoken)
    print(obj.get_time_spent('12194'))



