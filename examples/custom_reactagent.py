from typing import Any, Literal

from llama_index.core.agent.react import ReActChatFormatter, ReActOutputParser
from llama_index.core.agent.react.types import (
    ActionReasoningStep,
    ObservationReasoningStep,
)
from llama_index.core.llms import ChatMessage
from llama_index.core.llms.llm import LLM
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import ToolSelection
from llama_index.core.tools.types import BaseTool
from llama_index.core.workflow import (
    Context,
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)


class PrepEvent(Event):
    pass


class InputEvent(Event):
    input: list[ChatMessage]


class ToolCallEvent(Event):
    tool_calls: list[ToolSelection]


# === only for message or log ===
# class AnswerStream(Event):
#     delta: str

# class ToolCallMessage(Event):
#     info: str


class StreamEvent(Event):
    """content can be answer or tool call"""

    delta: str


class ToolCallResultMessage(Event):
    output: str



class StopSignal(Event):
    pass


class ReActAgent(Workflow):
    def __init__(
        self,
        *args: Any,
        llm: LLM | None = None,
        tools: list[BaseTool] | None = None,
        extra_context: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.tools = tools or []
        self.llm = llm
        self.formatter = ReActChatFormatter.from_defaults(context=extra_context or "")
        self.output_parser = ReActOutputParser()

    @step
    async def new_user_msg(self, ctx: Context, ev: StartEvent) -> PrepEvent:
        """init prompt and memory"""
        # clear sources
        await ctx.set("sources", [])

        # init memory if needed
        memory = await ctx.get("memory", default=None)
        if not memory:
            memory = ChatMemoryBuffer.from_defaults(llm=self.llm)

        # get user input
        user_input = ev.input
        user_msg = ChatMessage(role="user", content=user_input)
        memory.put(user_msg)

        # clear current reasoning
        await ctx.set("current_reasoning", [])

        # set memory
        await ctx.set("memory", memory)

        return PrepEvent()

    @step
    async def prepare_chat_history(self, ctx: Context, ev: PrepEvent) -> InputEvent:
        # get chat history
        memory: ChatMemoryBuffer = await ctx.get("memory")
        chat_history = memory.get()
        current_reasoning = await ctx.get("current_reasoning", default=[])

        # format the prompt with react instructions
        llm_input = self.formatter.format(self.tools, chat_history, current_reasoning=current_reasoning)

        ctx.write_event_to_stream(InputEvent(input=llm_input))
        return InputEvent(input=llm_input)

    @step
    async def handle_llm_input(self, ctx: Context, ev: InputEvent) -> ToolCallEvent | StopEvent | PrepEvent:
        chat_history = ev.input
        current_reasoning = await ctx.get("current_reasoning", default=[])
        memory = await ctx.get("memory")

        response_gen = await self.llm.astream_chat(chat_history)
        async for response in response_gen:
            ctx.write_event_to_stream(StreamEvent(delta=response.delta or ""))

        try:
            reasoning_step = self.output_parser.parse(response.message.content)
            current_reasoning.append(reasoning_step)

            if reasoning_step.is_done:
                memory.put(ChatMessage(role="assistant", content=reasoning_step.response))
                await ctx.set("memory", memory)
                await ctx.set("current_reasoning", current_reasoning)

                sources = await ctx.get("sources", default=[])

                ctx.write_event_to_stream(StopSignal())
                return StopEvent(
                    result={
                        "response": reasoning_step.response,
                        "sources": [sources],
                        "reasoning": current_reasoning,
                    }
                )
            elif isinstance(reasoning_step, ActionReasoningStep):
                tool_name = reasoning_step.action
                tool_args = reasoning_step.action_input
                return ToolCallEvent(
                    tool_calls=[
                        ToolSelection(
                            tool_id="fake",
                            tool_name=tool_name,
                            tool_kwargs=tool_args,
                        )
                    ]
                )

        except Exception as e:
            current_reasoning.append(
                ObservationReasoningStep(observation=f"There was an error in parsing my reasoning: {e}")
            )
            await ctx.set("current_reasoning", current_reasoning)

        # if no tool calls or final response, iterate again
        return PrepEvent()

    @step
    async def handle_tool_calls(self, ctx: Context, ev: ToolCallEvent) -> PrepEvent:
        tool_calls = ev.tool_calls
        tools_by_name = {tool.metadata.get_name(): tool for tool in self.tools}
        current_reasoning = await ctx.get("current_reasoning", default=[])
        sources = await ctx.get("sources", default=[])

        # call tools -- safely!
        # for tool_call in tool_calls:
        tool_call = tool_calls[0]
        tool = tools_by_name.get(tool_call.tool_name)
        if not tool:
            current_reasoning.append(
                ObservationReasoningStep(observation=f"Tool {tool_call.tool_name} does not exist")
            )
        else:
            try:
                tool_output = tool(**tool_call.tool_kwargs)
                sources.append(tool_output)
                ctx.write_event_to_stream(ToolCallResultMessage(output=tool_output.content))
                current_reasoning.append(ObservationReasoningStep(observation=tool_output.content))

            except Exception as e:
                # this will never achived, assert tool is err-free(catch err inside)
                current_reasoning.append(
                    ObservationReasoningStep(observation=f"Error calling tool {tool.metadata.get_name()}: {e}")
                )

        # save new state in context
        await ctx.set("sources", sources)
        await ctx.set("current_reasoning", current_reasoning)

        # prep the next iteraiton
        return PrepEvent()


if __name__ == '__main__':
    from llama_index.utils.workflow import draw_all_possible_flows

    draw_all_possible_flows(ReActAgent, filename="my_workflow.html")