from dataclasses import dataclass
ROUTES={
'explain_document':['input','document','knowledge'], 'summarize_document':['input','document','knowledge'], 'extract_ideas':['input','document','knowledge','strategy'],
'research_topic':['input','research','knowledge'], 'build_video':['input','research','knowledge','strategy','story','hook','script','humanize','review','editor','production'],
'write_script':['input','research','knowledge','strategy','story','hook','script','humanize','review','editor','production'],
'improve_script':['input','knowledge','script','humanize','review','editor'], 'write_hook':['input','knowledge','hook','review'], 'analyze_text':['input','knowledge','review']}
@dataclass
class Plan: task_type:str; stages:list[str]
def plan(task): return Plan(task,ROUTES.get(task,ROUTES['build_video']))
