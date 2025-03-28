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


# ANSI 颜色代码
class Colors:
    GREEN = '\033[92m'
    RED = '\033[31m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    USER_PROMPT = YELLOW
    RESPONSE = GREEN


class CozeLLM(CustomLLM):
    context_window: int = 3900
    num_output: int = 256
    model_name: str = "coze_llm"
    # Initialize Coze client
    coze: Coze = coze
    conversation: Any = coze.conversations.create()
    bot_id: str = BOT_ID
    user_id: str = USER_ID

    # def __init__(self):
    #     super().__init__()
    #     logger.debug("CozeLLM initialized with bot_id: %s, user_id: %s, conversation_id: %s",
    #                 self.bot_id, self.user_id, self.conversation.id)

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
            print(f"{Colors.USER_PROMPT}User prompt: {prompt}{Colors.RESET}")
        response = chat_no_stream(prompt, self.bot_id, self.user_id, self.conversation.id)
        if logger.isEnabledFor(logging.DEBUG):
            print(f"{Colors.RESPONSE}Responce: {response}{Colors.RESET}")
        return CompletionResponse(text=response)

    @llm_completion_callback()
    def stream_complete(
        self, prompt: str, **kwargs: Any
    ) -> CompletionResponseGen:
        # 在调试模式下打印彩色提示
        if logger.isEnabledFor(logging.DEBUG):
            print(f"{Colors.USER_PROMPT}User prompt: {prompt}{Colors.RESET}")
        response = ""
        for c_type, token in chat_stream(prompt, self.bot_id, self.user_id, self.conversation.id):
            if c_type == 'content':
                if logger.isEnabledFor(logging.DEBUG):
                    print(f"{Colors.RESPONSE}{token}{Colors.RESET}", end="", flush=True)
                response += token
                yield CompletionResponse(text=response, delta=token)


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
    from .coze_llm import __name__ as coze_name
    from .utils import set_debug

    set_debug(coze_name, __name__)

    test_no_stream()
