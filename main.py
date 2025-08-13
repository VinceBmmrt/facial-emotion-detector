# main.py
from io import BytesIO
from typing_extensions import Literal
from pydantic import BaseModel, Field
import requests
import asyncio
from PIL import Image
from dotenv import load_dotenv
from autogen_agentchat.messages import MultiModalMessage
from autogen_core import Image as AGImage, CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.agents import AssistantAgent
from dataclasses import dataclass
from autogen_agentchat.messages import StructuredMessage


# Charger les variables d'environnement
load_dotenv(override=True)

@dataclass
class FaceEmotion(BaseModel):
    emotion: Literal["happy", "sad", "angry", "surprised", "neutral"]
    intensity: float = Field(..., ge=0.0, le=1.0) 
    age_estimate: int
    gender: Literal["male", "female", "other"]


async def main():
    # URL de l'image à analyser
    url = "https://as2.ftcdn.net/v2/jpg/00/56/93/53/1000_F_56935312_NiqxkRKOdGSJd86Tc2uLycL9fkUsIlRW.jpg"

    # Charger l'image
    pil_image = Image.open(BytesIO(requests.get(url).content))
    img = AGImage(pil_image)

      # Message initial multimodal
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


    # Client OpenAI
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

    # Agents
    description_agent = AssistantAgent(
        name="description_agent",
        model_client=model_client,
        system_message="You are good at describing images",
        # output_content_type=FaceEmotion,
    )
    evaluation_agent = AssistantAgent(
        name="evaluation_agent",
        model_client=model_client,
        system_message="Provide constructive feedback. Respond with 'APPROVE' when your feedback is addressed.",
    )

    # Condition d'arrêt : l'évaluateur dit "APPROVE"
    text_termination = TextMentionTermination("APPROVE")

    # Création de la team
    team = RoundRobinGroupChat(
        [description_agent, evaluation_agent],
        termination_condition=text_termination,
        max_turns=20
    )

    # Lancer la première analyse
    response = await description_agent.on_messages(
        [multi_modal_message], 
        cancellation_token=CancellationToken()
    )

    # Lancer l'interaction complète avec l'équipe
    result = await team.run(
        task=multi_modal_message, 
        cancellation_token=CancellationToken()
    )

    # Afficher les échanges
    for message in result.messages:
        print(f"{message.source}:\n{message.content}\n")  # type: ignore

if __name__ == "__main__":
    asyncio.run(main())
