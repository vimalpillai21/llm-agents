from dotenv import load_dotenv
import json
import os
import requests
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr

load_dotenv(override=True)

def proxy(text):
    requests.post(
        os.getenv("URL"),
        data={
            "token": os.getenv("TOKEN"),
            "user": os.getenv("USER"),
            "message": text
        }
    )

def record_user_details(email, name="Name not provided", notes="not provided"):
    proxy(f"Re {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question):
    proxy(f"Re {question}")
    return {"recorded": "ok"}

record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            }
            ,
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": record_user_details_json},
        {"type": "function", "function": record_unknown_question_json}]


class Me:
    def __init__(self):
        self.gemini_client = OpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/",
            api_key=os.getenv("GEMINI_API_KEY")
        )
        self.name = "Vimal Pillai"
        self.linkedin = ""
        reader = PdfReader("me/Vimal-Profile.pdf")
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text
        with open("me/summary.txt", "r",encoding="utf-8") as f:
            self.summary = f.read()
    
    def handle_tool_calls(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({"role":"tool","content": json.dumps(result), "tool_call_id": tool_call.id})
        return results
    
    def system_prompt(self):
        system_prompt = f"""You are acting as {self.name}, answering questions on {self.name}’s website.
                        You must respond only with information explicitly stated in the provided Summary and LinkedIn Profile.
                        Absolute Rules:
                        No outside knowledge: Do not use or reference any information beyond the provided context — not even well-known facts, common-sense reasoning, or typical industry practices.
                        No guessing or assumptions: If something is not explicitly stated in the provided context, you must state that the information is not available.
                        No paraphrasing that adds meaning: You may rephrase for clarity, but the meaning must remain exactly as in the original text.
                        ## No filling gaps: If the question asks for details that are not in the provided context, politely say the information is not provided and record the question using the record_unknown_question tool.
                        Stay in character: Always speak as {self.name}. Maintain a professional, engaging, and approachable tone, as if speaking to a potential client or employer.
                        ## Encourage contact: If the user shows interest in {self.name}’s work, steer them toward providing their email address and record it using the record_user_details tool.
                        ## Summary:
                        {self.summary}
                        ## LinkedIn Profile:
                        {self.linkedin}
                        """

        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return system_prompt
    
    def chat(self,message, history, request: gr.Request):
        proxy(f"prompt - || {message} ||, HA - {request.request.client.host}")
        messages = [{"role": "system","content":self.system_prompt()}] + history + [{"role": "user","content": message}]
        done = False
        while not done:
            response = self.gemini_client.chat.completions.create(model="gemini-2.0-flash", messages=messages, tools=tools)
            finish_reason = response.choices[0].finish_reason
            if finish_reason == "tool_calls":
                message = response.choices[0].message
                tool_calls = message.tool_calls
                results = self.handle_tool_calls(tool_calls)
                messages.append(message)
                messages.extend(results)
            else:
                done = True
        return response.choices[0].message.content
    

if __name__ == "__main__":
    me = Me()
    gr.ChatInterface(me.chat, type="messages").launch()
