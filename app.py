from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
import time

app = FastAPI()

# Load OpenAI API key from environment variable
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise EnvironmentError("No OPENAI_API_KEY found in environment")

client = OpenAI(api_key=api_key)

# Model for user input
class UserInput(BaseModel):
    message: str

# Global variables to store assistant and thread information
assistant_id = None
thread_id = None


async def startup_event():
    global assistant_id, thread_id
    # Create file for knowledge retrieval (modify as needed)
    file = client.files.create(file=open("seedworld_website.txt", "rb"), purpose='assistants')
    # Create the assistant
    '''
    assistant = client.beta.assistants.create(
        name="seedworld greeter",
        description="you are seedworld greeter, answer questions about seedworld",
        model="gpt-4-1106-preview",
        tools=[{"type": "retrieval"}],
        file_ids=[file.id]
    )'''
    assistant_id = "asst_jghYoFw67tKaQ056C902Mp2z"
    # Create a new thread
    thread = client.beta.threads.create()
    thread_id = thread.id

app.add_event_handler("startup", startup_event)

@app.post("/ask/")
async def ask_question(input: UserInput):
    global thread_id, assistant_id
    if not thread_id or not assistant_id:
        raise HTTPException(status_code=500, detail="Assistant or Thread not initialized")

    # Send the user message to the thread
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=input.message
    )

    # Execute the thread run
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    # Wait for the response to be generated
    #time.sleep(6)  # Adjust the sleep time as needed

    # Retrieve the latest messages from the thread
    messages = client.beta.threads.messages.list(
        thread_id=thread_id,
    )

    # Format and return the conversation
    conversation = [{"role": msg.role, "content": msg.content[0].text.value} for msg in reversed(messages.data)]
    return {"conversation": conversation}

@app.get("/get_thread/")
async def get_thread():
    global thread_id
    if not thread_id:
        raise HTTPException(status_code=500, detail="Thread not initialized")

    # Retrieve the latest messages from the thread
    messages = client.beta.threads.messages.list(
        thread_id=thread_id,
    )

    # Format and return the conversation
    conversation = [{"role": msg.role, "content": msg.content[0].text.value} for msg in reversed(messages.data)]
    return {"conversation": conversation}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)