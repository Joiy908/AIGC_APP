import logging
from typing import Any

from cozepy import Coze
from llama_index.core.llms import (
    CompletionResponse,
    CompletionResponseGen,
    CustomLLM,
    LLMMetadata,
)
from llama_index.core.llms.callbacks import llm_completion_callback

from .coze_llm import BOT_ID, USER_ID, chat_no_stream, chat_stream, coze

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# ANSI 颜色代码
class Colors:
    GREEN = '\033[92m'  # 绿色用于提示
    RESET = '\033[0m'   # 重置颜色

class CozeLLM(CustomLLM):
    context_window: int = 3900
    num_output: int = 256
    model_name: str = "coze_llm"
    # Initialize Coze client
    coze: Coze = coze
    conversation: Any = coze.conversations.create()
    bot_id: str = BOT_ID
    user_id: str = USER_ID

    def __init__(self):
        super().__init__()
        logger.debug("CozeLLM initialized with bot_id: %s, user_id: %s, conversation_id: %s",
                    self.bot_id, self.user_id, self.conversation.id)

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
        # 在调试模式下打印彩色提示
        if logger.isEnabledFor(logging.DEBUG):
            print(f"{Colors.GREEN}User prompt: {prompt}{Colors.RESET}")
        logger.debug("Starting non-streaming completion for prompt: %s", prompt)
        response = chat_no_stream(prompt, self.bot_id, self.user_id, self.conversation.id)
        logger.debug("Non-streaming completion received: %s", response)
        return CompletionResponse(text=response)

    @llm_completion_callback()
    def stream_complete(
        self, prompt: str, **kwargs: Any
    ) -> CompletionResponseGen:
        # 在调试模式下打印彩色提示
        if logger.isEnabledFor(logging.DEBUG):
            print(f"{Colors.GREEN}User prompt: {prompt}{Colors.RESET}")
        logger.debug("Starting streaming completion for prompt: %s", prompt)
        response = ""
        for c_type, token in chat_stream(prompt, self.bot_id, self.user_id, self.conversation.id):
            if c_type == 'content':
                response += token
                logger.debug("Stream token received: %s", token)
                yield CompletionResponse(text=response, delta=token)
        logger.debug("Streaming completion finished with full response: %s", response)

def test_stream():
    llm = CozeLLM()
    completions = llm.stream_complete("Paul Graham is ")
    for completion in completions:
        print(completion.delta, end="", flush=True)
    print()

def test_no_stream():
    llm = CozeLLM()
    res = llm.complete("hello")
    print(res)



if __name__ == "__main__":
    # 设置调试模式（可通过命令行或环境变量控制）
    logger.setLevel(logging.DEBUG)
    print("Running in DEBUG mode")
    
    test_no_stream()