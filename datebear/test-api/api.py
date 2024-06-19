import uvicorn
from fastapi import FastAPI, Request
import sys
sys.path.append('../haystack_qa')
import haystack_qa
app = FastAPI()

current_chat = []
client = haystack_qa.get_client()
@app.get("/")
async def root():
    return {"message": "Hello World!!!"}

@app.get("/answer")
def first_example():
  return {"response": "heyy"}

@app.post("/chatpost")
async def get_question(request: Request):
    data = await request.json()
    messages = data.get("messages", "")
    messages = get_answer(messages)
    return {"messages": messages}

@app.get("/chatanswer")
def get_answer(messages):
    mapped_messages = haystack_qa.map_dict_haystack_msgs(messages)
    res_messages = haystack_qa.get_response(mapped_messages)
    return {"messages": res_messages}



@app.get("/initchat")
def init_chat():
    messages = haystack_qa.init_chat(client)
    return {"messages": messages}


print(init_chat())