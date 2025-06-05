from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import os
import json

client = OpenAI()

def run_command(cmd:str):
    res = os.system(cmd)
    return res

available_tools = {
    "run_command":run_command
}

SYSTEM_PROMPT = """
    you are an AI agent that builds projects for user straight from the CLI . 
    You need to follow the following steps : start , plan, action ,observe. 

    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.

    # Make sure you never give commands for removing anything from system files . 

    Available Tools:
    1. "run_command":Takes linux command as a string and executes the command and returns the output after executing it.
    
   Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query

    Output Format : 
    {{
        "step" : "string",
        "function" : "string",
        "input" : "string",
        "content" : "string"
    }}

    Example:
    User: Create a folder named raju
    Output : {{"step":"start","content":"User wants me to create a folder named raju so looking for an available tool to help me"}}
    Output : {{"step":"plan","content":"I have a tool 'run_command' that can help in this query"}}
    Output : {{"step":"action","function":"run_command","input":"mkdir raju"}}
    Output : {{"step":"observe","content":"the folder has been created"}}
    Output : {{"step":"result","content":"Folder created Successfully ."}}
    
"""
messages = [{"role":"system","content":SYSTEM_PROMPT}]
while True:
    query = input("Enter: ")
    messages.append({"role":"user","content":query})
    while True:
        response = client.chat.completions.create(
            model = "gpt-4o",
            response_format = {"type":"json_object"},
            messages = messages,
        )
        # ai ko bhjne ke liye string me convert kerdiya
        # json me repsonse milra hai AI se to direct store kerliya obj me
        obj = json.loads(response.choices[0].message.content)
        messages.append({"role":"assistant","content":response.choices[0].message.content})
        
        step = obj["step"]
        content = obj.get("content")
        print(response.choices[0].message.content)

        if step == "action":
            result = available_tools[obj["function"]](obj.get("input"))
            messages.append({ "role": "assistant", "content": json.dumps({ "step": "observe", "content": result }) })
            continue
        if step == "result":
            print("🤖: ",content)
            break

