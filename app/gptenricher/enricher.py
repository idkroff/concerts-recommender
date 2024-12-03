from yandex_cloud_ml_sdk import YCloudML
from app.models.common import Concert
import os
import json
import re
from pathlib import Path

import logging
logger = logging.getLogger(__name__)


class GPTEnricher:
    def __init__(self):
        self.system_prompt = self.load_json(
            Path("training_data/system_prompt.json"))["text"]
        logger.debug(f'using system prompt: {self.system_prompt}')

        token = os.getenv("GPT_ENRICHER_API_TOKEN")
        if token is None:
            raise Exception("token not found in env GPT_ENRICHER_API_TOKEN")

        folder_id = os.getenv("GPT_ENRICHER_FOLDER_ID")
        model = os.getenv("GPT_ENRICHER_MODEL")
        if folder_id is None and model is None:
            raise Exception(
                "folder_id and model both not found in env GPT_ENRICHER_FOLDER_ID, GPT_ENRICHER_MODEL")

        model_temperature = os.getenv("GPT_ENRICHER_MODEL_TEMPERATURE")
        if model_temperature is not None:
            model_temperature = float(model_temperature)
        else:
            model_temperature = 0.5

        sdk = YCloudML(folder_id=folder_id, auth=token)

        if model is not None:
            self.model = sdk.models.completions(model)
        else:
            logger.info(
                "[init] model not provided, using yandexgpt-rc by default")
            self.model = sdk.models.completions(
                "yandexgpt", model_version="rc")

        self.model = self.model.configure(temperature=model_temperature)

    def enrich(self, user_input: str, concerts: list[Concert], distribution: dict[str, int]) -> str:
        concerts = sorted(
            concerts, key=lambda c: distribution[c.artist.name], reverse=True)
        concerts_dicts = [concert.to_dict() for concert in concerts]

        request = {
            "concerts": concerts_dicts,
            "artists_distribution": distribution,
            "user_request": user_input.strip()
        }

        result = self.model.run([
            {"role": "system", "text": self.system_prompt},
            {"role": "user", "text": json.dumps(request, ensure_ascii=False)}
        ])

        logger.debug(f"[enrich] executing request: {request}")

        output = result[0].text
        output = self.render_emoji(output)

        if user_input == "":
            output = self.remove_recommendation_labels(output)

        return output

    def render_emoji(self, text: str) -> str:
        text = text.replace("[music_icon]", "🎶")
        text = text.replace("[date_icon]", "📅")
        text = text.replace("[ticket_icon]", "🔖")
        text = text.replace("[place_icon]", "📍")
        return text

    def remove_recommendation_labels(self, text: str) -> str:
        return re.sub(r'\/\/ Подходит под запрос.*$', '', text)

    def load_json(self, path: Path):
        module_path = Path(__file__).parent
        file_path = module_path / path

        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data
