import config
import openai
from openai import AsyncOpenAI
import logging
logger = logging.getLogger(__name__)

aclient = AsyncOpenAI(api_key=config.openai_api_key, base_url=config.openai_api_base)

OPENAI_COMPLETION_OPTIONS = {
    "temperature": 0,
    "max_tokens": 1000,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "timeout": 150.0,
}

class ChatGPT:
    def __init__(self):
        self.model = config.models["current_model"]

    async def send_message(self, message, dialog_messages=[], chat_mode="general_english"):
        if chat_mode not in config.chat_modes.keys():
            raise ValueError(f"Chat mode {chat_mode} is not supported")

        n_dialog_messages_before = len(dialog_messages)
        answer = None
        while answer is None:
            try:
                if self.model in {"gpt-3.5-turbo-16k", "gpt-3.5-turbo", "gpt-4", "gpt-4-1106-preview"}:
                    messages = self._generate_prompt_messages(message, dialog_messages, chat_mode)
                    # logger.error('messages')
                    # logger.error(messages)
                    r = await aclient.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        **OPENAI_COMPLETION_OPTIONS
                    )
                    answer = r.choices[0].message.content
                else:
                    raise ValueError(f"Unknown model: {self.model}")

                answer = self._postprocess_answer(answer)
                n_input_tokens, n_output_tokens = r.usage.prompt_tokens, r.usage.completion_tokens
            except openai.OpenAIError as e:  # too many tokens
                if len(dialog_messages) == 0:
                    raise ValueError("Dialog messages is reduced to zero, but still has too many tokens to make completion") from e

                # forget first message in dialog_messages
                dialog_messages = dialog_messages[1:]

        n_first_dialog_messages_removed = n_dialog_messages_before - len(dialog_messages)

        return answer, (n_input_tokens, n_output_tokens), n_first_dialog_messages_removed

    def _generate_prompt_messages(self, message, dialog_messages, chat_mode):
        prompt = config.chat_modes[chat_mode]["prompt_start"]

        messages = [{"role": "system", "content": prompt}]
        for dialog_message in dialog_messages:
            messages.append({"role": "user", "content": dialog_message["user"]})
            messages.append({"role": "assistant", "content": dialog_message["bot"]})
        messages.append({"role": "user", "content": message})

        return messages

    def _postprocess_answer(self, answer):
        answer = answer.strip()
        return answer

async def transcribe_audio(audio_file) -> str:
    r = await aclient.audio.transcriptions.create(model="whisper-1", file=audio_file, language="en")
    return r.text or ""

async def generate_audio(text, speech_file_path):
    response = await aclient.audio.speech.create(
        model="tts-1", voice="nova", input=text
    )
    await response.astream_to_file(speech_file_path)

OPENAI_DICT_COMPLETION_OPTIONS = {
    "temperature": 0.2,
    "max_tokens": 500,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "timeout": 150.0,
}

async def dictionary(text):
    prompt = config.chat_modes["dictionary"]["prompt_start"]

    messages = [{"role": "system", "content": prompt}]
    messages.append({"role": "user", "content": text})
    r = await aclient.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        **OPENAI_DICT_COMPLETION_OPTIONS
    )
    answer = r.choices[0].message.content
    return answer
