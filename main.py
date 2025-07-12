from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import os
import json

client = OpenAI()
print("WELCOME TO MINI COMMAND LINE BASED CURSOR !")

def run_command(cmd:str):
    res = os.system(cmd)
    print(res)
    return res

def write_code(file_name, input):
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    
    # Write content to file
    with open(file_name, 'w') as f:
        f.write(input)
    
    return f"Code written to {file_name}"


available_tools = {
    "run_command":run_command,
    "write_code":write_code
}

SYSTEM_PROMPT = """

    you are an AI agent that builds projects for user straight from the CLI or if user asks simple question and doesn;t ask you to do anything , just simply give him the answer no need to follow the steps mentioned below.
    You need to follow the following steps : start , plan, action ,observe. 

    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.

    NEVER use `rm`, `sudo`, or delete system files.

    Available Tools:
    1. "run_command":Takes linux command as a string and executes the command and returns the output after executing it.
    2. "write_code":Takes a file_name and code , and write that code in the particular file
    
   Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query
    - NEVER use `rm`, `sudo`, or delete system files.

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

    Example:
    User: Create a todo app in react .
    
    you should run "npm create vite@latest {{name if mentioned by user otherwise my-app}} -- --template react"
    or
    if user mentions typescript : "npm create vite@latest {{name if mentioned by user otherwise my-app}} -- --template react-ts"

    then start writing code for making a todo application file by file as needed , follow proper Component structure and make sure to place them inside App file.
    
    make sure to run npm install, then run the server using command : "cd {{name of project}} && npm run dev"

    User: Create a hello world program in react .
    Output: {{"step":"start","content":"User wants me to create a react app and make a hello world page in it ."}}
    Output:{{"step":"plan","content":"I have a tool called 'run_command' that can help me setup react project"}}
    Output :{{"step":"action","function":"run_command","input":"npm create vite@latest hello-world-app (or any other name you feel appropriate , unless explicitely specified by user) -- --template react"}}
    Output: {{"step":"plan","content":"now that the folder structure is ready I need to navigate to the appropriate folder and install the dependencied first . I can use a tool called 'run_command' "}}
    Output: {{"step":"action","function":"run_command","input":"cd hello-world-app && npm i"}}
    Output: {{"step":"action","function":"run_command","input":"cd hello-world-app"}} 
    Output: {{"step":"plan","content":"now that the dependencies are setup I need to navigate to the appropriate file and write code in it . I can use a tool called 'write_code'"}}
    Output: {{"step":"action","function":"write_code","file_name":"hello-world-app/src/App.jsx","input":"import React from 'react'
            function App() {
                return (
                    <div>
                    Hello World
                    </div>
                )
            }
            export default App"}}
    Output: {{"step":"plan","content":"Now I have completed all the things mentioned in the prompt so , i will just start the project now, i have a tool 'run_command' that I can use to start the project. "}}
    Output: {{"step":"action","function":"run_command","input":"cd hello-world-app && npm run dev"}}
    Output : {{"step":"observe","content":"The App has been created completely"}}


"""
messages = [{"role":"system","content":SYSTEM_PROMPT}]
while True:
    query = input("Enter the query: ")
    messages.append({"role" : "user","content" : query})
    while True:
        response = client.chat.completions.create(
            model = "gpt-4o",
            response_format = {"type":"json_object"},
            messages = messages,
        )
        # ai ko simply bhej diya aage json string me hi
        # json string me repsonse milra hai AI se to convert kerliya python object me
        obj = json.loads(response.choices[0].message.content)
        messages.append({"role":"assistant","content":response.choices[0].message.content})
        
        step = obj["step"]
        content = obj.get("content")
        print(response.choices[0].message.content)

        if step == "action":
            function_to_call = obj["function"]
            global result
            if function_to_call == "run_command":
                result = available_tools[function_to_call](obj.get("input"))
            else:
                result = available_tools[function_to_call](obj.get("file_name"),obj.get("input"))
            messages.append({ "role": "assistant", "content": json.dumps({ "step": "observe", "content": result }) })
            continue
        if step == "result":
            print("🤖: \n",content)
            break

