import openai
import re
import httpx
import os
from dotenv import load_dotenv

_ = load_dotenv()
from openai import OpenAI


client = OpenAI()
# chat_completion = client.chat.completions.create(
#     model="gpt-3.5-turbo",
#     messages=[{"role": "user", "content": "Hello world"}]
# )
# chat_completion.choices[0].message.content

prompt = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

calculate:
e.g. calculate: 4 * 7 / 3
Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

average_dog_weight:
e.g. average_dog_weight: Collie
returns average weight of a dog when given the breed

Example session:

Question: How much does a Bulldog weigh?
Thought: I should look the dogs weight using average_dog_weight
Action: average_dog_weight: Bulldog
PAUSE

You will be called again with this:

Observation: A Bulldog weights 51 lbs

You then output:

Answer: A bulldog weights 51 lbs
""".strip()

class agent:
    def __init__(self,system =''):
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})
            
    def __call__(self,messages):
        self.messages.append({"role":"user","content":messages})
        result = self.execute()
        self.messages.append({"role":"system",'content':result})
        return result
        
    def execute(self):
        completion = client.chat.completions.create(
                        model="gpt-4o", 
                        temperature=0,
                        messages=self.messages)
        return completion.choices[0].message.content
    
    
def calculate(what):
    return eval(what)

def average_dog_weight(name):
    if name in "Scottish Terrier": 
        return("Scottish Terriers average 20 lbs")
    elif name in "Border Collie":
        return("a Border Collies average weight is 37 lbs")
    elif name in "Toy Poodle":
        return("a toy poodles average weight is 7 lbs")
    else:
        return("An average dog weights 50 lbs")

known_actions = {
    "calculate": calculate,
    "average_dog_weight": average_dog_weight
}



# agent = agent(system = prompt)
action_re = re.compile('^Action: (\w+): (.*)$')

def query(question,max_turns = 5):
    i = 0
    bot = agent(prompt)
    next_prompt = question
    while i< max_turns:
        i+= 1
        print("next_prompt ",next_prompt)
        result = bot(next_prompt)
        print("result",result)
        actions =[
            action_re.match(a)
            for a in result.split('\n')
            if action_re.match(a)
        ]
        print(f"action for iteration {i} is {actions}")
        if actions:
            action,action_input = actions[0].groups()
            if action not in known_actions:
                raise Exception(f"unknown action: {action}:{action_input}")
                
            print(f"----runnning action : {action}, action_input: {action_input}")
            observation = known_actions[action](action_input)
            next_prompt = f"Observation: {observation}"
        else:
            return 
    
if __name__ == "__main__":
    question = """I have 2 dogs, a border collie and a scottish terrier. \
What is their combined weight"""
    query(question)