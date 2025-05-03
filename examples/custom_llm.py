import logging
from collections.abc import Sequence
from typing import Any

from cozepy import AsyncCoze, Coze
from llama_index.core.base.llms.types import (
    ChatMessage,
    ChatResponse,
    ChatResponseAsyncGen,
    CompletionResponse,
    MessageRole,
)
from llama_index.core.llms import (
    CompletionResponseGen,
    CustomLLM,
    LLMMetadata,
)
from llama_index.core.llms.callbacks import llm_chat_callback, llm_completion_callback

from .async_coze_llm import achat_stream, acoze
from .coze_llm import BOT_ID, USER_ID, chat_no_stream, chat_stream, coze
from .utils import Colors

# Configure logging
logger = logging.getLogger(__name__)


class CozeLLM(CustomLLM):
    context_window: int = 3900
    num_output: int = 256
    model_name: str = "coze_llm"
    # Initialize Coze client
    coze: Coze = coze
    acoze: AsyncCoze = acoze
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
    def stream_complete(self, prompt: str, **kwargs: Any) -> CompletionResponseGen:
        # 在调试模式下打印彩色提示
        if logger.isEnabledFor(logging.DEBUG):
            print(f"{Colors.USER_PROMPT}User prompt: {prompt}{Colors.RESET}")
        response = ""
        for c_type, token in chat_stream(prompt, self.bot_id, self.user_id, self.conversation.id):
            if c_type == "content":
                if logger.isEnabledFor(logging.DEBUG):
                    print(f"{Colors.RESPONSE}{token}{Colors.RESET}", end="", flush=True)
                response += token
                yield CompletionResponse(text=response, delta=token)

    @llm_chat_callback()
    async def astream_chat(
        self,
        messages: Sequence[ChatMessage],
        **kwargs: Any,
    ) -> ChatResponseAsyncGen:
        # astream_complete + astream_chat
        async def gen() -> ChatResponseAsyncGen:
            assert self.messages_to_prompt is not None
            prompt = self.messages_to_prompt(messages)

            if logger.isEnabledFor(logging.DEBUG):
                print(f"{Colors.USER_PROMPT}User prompt: {prompt}{Colors.RESET}")
            response = ""
            async for c_type, delta in achat_stream(prompt, self.bot_id, self.user_id, self.conversation.id):
                if c_type == "content":
                    response += delta
                    if logger.isEnabledFor(logging.DEBUG):
                        print(f"{Colors.RESPONSE}{delta}{Colors.RESET}", end="", flush=True)
                    yield ChatResponse(
                        message=ChatMessage(
                            role=MessageRole.ASSISTANT,
                            content=response,
                        ),
                        delta=delta,
                        raw=response,
                    )

        return gen()


async def test_achat_stream():
    llm = CozeLLM()
    completions = await llm.astream_chat(messages=[ChatMessage(content="Hi, what's your name?")])
    async for completion in completions:
        print(completion.delta, end="", flush=True)
    print()


async def test_astream():
    llm = CozeLLM()
    completions = await llm.astream_complete("Paul Graham is ")
    async for completion in completions:
        print(completion.delta, end="", flush=True)
    print()


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


async def amain():
    # await test_astream()
    await test_achat_stream()


if __name__ == "__main__":
    # 设置调试模式（可通过命令行或环境变量控制）
    # from .coze_llm import __name__ as coze_name
    # from .utils import set_debug

    # set_debug(coze_name, __name__)

    # test_stream()
    import asyncio

    asyncio.run(amain())
