from dataclasses import dataclass
from haystack.dataclasses import ChatMessage, ChatRole
from haystack.components.generators.chat import OpenAIChatGenerator
import json
from haystack.utils import Secret

##### Mapping Function

def map_dict_haystack_msgs(messages_dict_list):
    msgs = [
    ChatMessage(x["content"], ChatRole(x["role"]), x.get("name")) 
    for x in messages_dict_list
    ]
    return msgs


##### Define Tools
####Tool class 
@dataclass
class Tool:
    function:object
    tool_dict:dict

def get_client():
    return OpenAIChatGenerator(api_key=Secret.from_token("sk-proj-ASz5PzsxbFKArnEwawfuT3BlbkFJYvP7KdEolmDspdAIu5T6"))

client = get_client()

def get_current_weather(location: str, unit: str = "celsius"):
  return {"weather": "sunny", "temperature": 21.8, "unit": unit}

def get_order_by_number(order_number, file_path='../../data/order_data.json'):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            
            for order in data:
                if order['orderNumber'] == order_number:
                    return order
            return None
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON from file.")
        return None


weather_tool = Tool(
    function= get_current_weather,
    tool_dict={
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                },
                "required": ["location", "unit"],
            },
        }
    }
)

order_info_tool = Tool(
    function=get_order_by_number,
    tool_dict={
    "type": "function",
    "function": {
        "name": "get_order_by_number",
        "description": "Retrieve an order by its order number from a JSON file.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_number": {
                    "type": "string",
                    "description": "The 8-digit order number to search for."
                },
                "file_path": {
                    "type": "string",
                    "description": "The path to the JSON file containing order data.",
                    "default": "../../data/order_data.json"
                }
            },
            "required": ["order_number"]
        }
    }
    }
)

available_functions = {"get_current_weather":weather_tool.function,"get_order_by_number":get_order_by_number}
tools = [weather_tool.tool_dict,order_info_tool.tool_dict]



##### Get Tool answer

def use_tool(response):
    function_call = json.loads(response["replies"][0].content)[0]
    function_name = function_call["function"]["name"]
    function_args = json.loads(function_call["function"]["arguments"])
    print("function_name:", function_name)
    print("function_args:", function_args)
    function_to_call = available_functions[function_name]
    function_response = function_to_call(**function_args)
    function_message = ChatMessage.from_function(content=json.dumps(function_response), name=function_name)
    print(function_message)
    return function_message

##### Function to create current chat
def init_chat(client):
    messages = []
    messages.append(ChatMessage.from_system("Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."))
    return messages






##### Add User Input to Chat and return answer
def get_response(messages):
    response = client.run(
        messages=messages,
        generation_kwargs={"tools":tools}
    )
    if response and response["replies"][0].meta["finish_reason"] == 'tool_calls':
        function_calls = json.loads(response["replies"][0].content)
        for function_call in function_calls:
            function_name = function_call["function"]["name"]
            function_to_call = available_functions[function_name]
            function_args = json.loads(function_call["function"]["arguments"])

            function_response = function_to_call(**function_args)
            function_message = ChatMessage.from_function(content=json.dumps(function_response), name=function_name)
            print(messages)
            messages.append(function_message)
            response = client.run(
                messages=messages,
                generation_kwargs={"tools":tools}
                )
    messages.append(ChatMessage.from_assistant(response["replies"][0].content))
    return messages

