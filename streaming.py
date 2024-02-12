from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import os
from openai import OpenAI

app = FastAPI()

api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise EnvironmentError("No OPENAI_API_KEY found in environment")

client = OpenAI(api_key=api_key)

@app.get("/stream_gpt_response/")
async def stream_gpt_response(user_input: str):
    async def event_generator():
        # Make a streaming request to OpenAI API
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_input}],
                stream=True
            )

            # Stream the response chunks
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield f"data: {chunk.choices[0].delta.content}\n\n"

        except Exception as e:
            yield f"data: Error - {str(e)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")