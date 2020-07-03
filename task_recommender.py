from jira import JIRA
import datetime
import pickle
import os
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
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
        try:
            for project in projects_list:
                try:
                    all_project_issues = self.get_issues(project)
                except Exception as e:
                    #print(e)
                    continue
                for issue in all_project_issues:
                    try:
                        time_diff = self.get_time_spent(issue.id)
                        issues_list.append((issue.id,issue.raw['fields']['summary'],time_diff,issue.raw['fields']['updated'].split('+')[0]))
                    except Exception as e:
                        #print(e)
                        continue
        except Exception as e:
            #print(e)
            pass
        finally:
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

            return (time_difference.seconds//3600) * 8

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

    def unpickle_data(self,filename):
        "Unpickle and return the obj"
        pobj = None
        with open(filename,'rb') as pf:
            pobj = pickle.load(pf)

        return pobj

    def check_pickle_available(self,filename):
        "Check if a pickle avail"
        if_avail = False
        if os.path.exists(filename):
            if_avail = True
        
        return if_avail

    def create_dataframe(self,df_name,columns):
        "Create a Pandas DataFrame"
        df = pd.DataFrame(df_name,columns=columns)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_colwidth', -1)

        return df

    def collect_jira_data(self,keyword):
        "Collect JIRA data for a keyword"
        if self.check_pickle_available(keyword):
            #print("Pickle obj found")
            issues_list = self.unpickle_data(keyword)
        else:
            projects = self.get_projects_using_keyword(keyword)
            #print("Obtained projects")
            issues_list = self.get_issues_from_projects(projects)
            self.pickle_data(issues_list,keyword)

        df = self.create_dataframe(issues_list,columns=['issue_id','summary','time_taken','time_stamp'])

        return df

    def plot_network_graph(self,data_frame,keyword):
        "Plat a network graph"
        data_frame = data_frame.sort_values(by=['time_stamp'])
        graph = nx.path_graph(len(data_frame))
        tasks = {}
        for i in range(0,len(data_frame) -1):
            tasks[i] = data_frame['summary'].iloc[i]

        H=nx.relabel_nodes(graph,tasks)
        for edge in H.edges():
            print(edge)
        nx.draw(H, with_labels=True, font_size=4)
        filename = keyword + '.png'
        plt.savefig(filename)
        plt.show()
    
if __name__ == '__main__':
    obj = LocalJira(server,username,apitoken)
    # Training data
    keyword = 'training'
    issues_df = obj.collect_jira_data(keyword)
    duplicate_df = issues_df[issues_df.duplicated(['summary'])]
    obj.plot_network_graph(duplicate_df,keyword)
    #duplicate_df = duplicate_df[duplicate_df['time_taken'].notna()]
    #print(duplicate_df.groupby(['summary']).mean().sort_values(by=['time_taken']))
    #print(duplicate_df['summary'][:10])

    # Onboarding data
    keyword = 'onboarding'
    issues_df = obj.collect_jira_data(keyword)
    duplicate_df = issues_df[issues_df.duplicated(['summary'])]
    obj.plot_network_graph(duplicate_df,keyword)
    #print(duplicate_df.sort_values(by=['time_stamp']))
    #duplicate_df = duplicate_df[duplicate_df['time_taken'].notna()]
    #print(duplicate_df.groupby(['summary']).mean().sort_values(by=['time_taken']))
    #print(duplicate_df['time_stamp'][:10])

