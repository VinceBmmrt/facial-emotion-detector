from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from PIL import Image
import json
import re

from autogen_core import Image as AGImage, CancellationToken
from autogen_agentchat.messages import MultiModalMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination

load_dotenv(override=True)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # à limiter en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agents & team (initialisés une seule fois)
model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

description_agent = AssistantAgent(
    name="description_agent",
    model_client=model_client,
    system_message="You are good at describing images"
)

evaluation_agent = AssistantAgent(
    name="evaluation_agent",
    model_client=model_client,
    system_message="Provide constructive feedback. Respond with 'APPROVE' when your feedback is addressed."
)

text_termination = TextMentionTermination("APPROVE")

team = RoundRobinGroupChat(
    [description_agent, evaluation_agent],
    termination_condition=text_termination,
    max_turns=20
)

async def analyze_pil_image(pil_image: Image.Image):
    pil_image = pil_image.convert("RGB")
    img = AGImage(pil_image)

    multi_modal_message = MultiModalMessage(
        content=[
            """Analyze the face in this image and respond ONLY with a valid JSON matching this format:
            {
                "emotion": "happy" | "sad" | "angry" | "surprised" | "neutral",
                "intensity": 0.0-1.0,
                "age_estimate": integer
            }
            Do not include any text outside of the JSON.""",
            img
        ],
        source="User"
    )

    # On lance d'abord le premier agent
    await description_agent.on_messages(
        [multi_modal_message],
        cancellation_token=CancellationToken()
    )

    # Puis la boucle avec l'équipe
    result = await team.run(
        task=multi_modal_message,
        cancellation_token=CancellationToken()
    )

    # On cherche le message de description_agent
    for message in reversed(result.messages):
        if message.source == "description_agent":
            raw_content = message.content if isinstance(message.content, str) else str(message.content) # type: ignore
            # Extraction sécurisée du JSON
            match = re.search(r"\{.*\}", raw_content, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    return None
    return None

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        img_bytes = await file.read()
        pil_image = Image.open(BytesIO(img_bytes))
        json_result = await analyze_pil_image(pil_image)
        if not json_result:
            return {"result": None, "error": "Impossible d'extraire le JSON"}
        return {"result": json_result}
    except Exception as e:
        return {"result": None, "error": str(e)}
