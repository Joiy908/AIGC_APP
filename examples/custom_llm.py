from typing import Any

from coze_llm import BOT_ID, USER_ID, chat_no_stream, chat_stream, coze
from cozepy import (
    Coze,
)
from llama_index.core.llms import (
    CompletionResponse,
    CompletionResponseGen,
    CustomLLM,
    LLMMetadata,
)
from llama_index.core.llms.callbacks import llm_completion_callback


class CozeLLM(CustomLLM):
    context_window: int = 3900
    num_output: int = 256
    model_name: str = "coze_llm"
    # Initialize Coze client
    coze: Coze = coze
    conversation: Any = coze.conversations.create()
    bot_id: str = BOT_ID
    user_id: str = USER_ID

    @property
    def metadata(self) -> LLMMetadata:
        """Get LLM metadata."""
        return LLMMetadata(
            context_window=self.context_window,
            num_output=self.num_output,
            model_name=self.model_name,
        )

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        return CompletionResponse(text=chat_no_stream(prompt, self.bot_id, self.user_id, self.conversation.id))

    @llm_completion_callback()
    def stream_complete(
        self, prompt: str, **kwargs: Any
    ) -> CompletionResponseGen:
        response = ""
        for c_type, token in chat_stream(prompt, self.bot_id, self.user_id, self.conversation.id):
            if c_type == 'content':
                response += token
                yield CompletionResponse(text=response, delta=token)



if __name__ == "__main__":
    llm = CozeLLM()
    completions = llm.stream_complete("Paul Graham is ")
    for completion in completions:
        print(completion.delta, end="")
