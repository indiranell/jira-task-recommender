from jira import JIRA
import conf

username = conf.username
apitoken = conf.apitoken
server = conf.server

class LocalJira(JIRA):
    def __init__(self,server,username,apitoken):
        super().__init__(server=server,basic_auth=(username,apitoken))

    def get_projects(self):
        return self.projects()


if __name__ == '__main__':
    obj = LocalJira(server,username,apitoken)
    print(dir(obj))
    print(obj.get_projects())


