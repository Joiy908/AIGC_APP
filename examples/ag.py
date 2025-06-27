import argparse
import platform
import sys

from llama_index.core.base.llms.types import ChatMessage

from .custom_llm import CozeLLM


def win_read_keyboard_input_multiline():
    import msvcrt
    buffer = ''
    return_count = 0
    while True:
        ch = msvcrt.getwch()
        if ch != '\r':
            return_count = 0

        if ch == '\r':
            return_count += 1
            print()
            if return_count >= 2:
                return buffer[:-1]
            else:
                buffer += '\n'
        elif ch == '\b':  # 退格键
            if buffer:
                buffer = buffer[:-1]
                # 删除控制台最后一个字符
                print('\b \b', end="", flush=True)
        elif ch == '\x03':  # Ctrl+C
            raise KeyboardInterrupt
        elif ch == '\x1a':  # Ctrl+Z（EOF）
            raise EOFError
        else:
            buffer += ch
            print(ch, end="", flush=True)


def read_keyboard_input():
    os = platform.system()
    if os == 'Windows':
        return win_read_keyboard_input_multiline()
    elif os == 'Linux':
        raise 'todo: impl Linux read from tty'
    else:
        raise 'Unsuppoted OS, please implment this method yourself'


def format_prompt(current_input: str, stdin_data: str = None) -> str:
    prompt = ''
    if stdin_data:
        prompt += f"\nstdin:\n{stdin_data}\n"
    prompt += f"\ncurrent user input:{current_input}\n"
    return prompt


def read_stdin():
    buffer = ''
    for line in sys.stdin:
        buffer += line
    return buffer


async def main(read_from_pipe):
    llm = CozeLLM()
    stdin_data = read_stdin() if read_from_pipe else ''

    question_count = 0
    while True:
        try:
            print("> ", end="", flush=True)
            curr_input = read_keyboard_input()
            if question_count == 0:
                prompt = format_prompt(curr_input, stdin_data)
            else:
                question_count += 1
                prompt = format_prompt(curr_input)

            # print('debug, prompt: ', prompt)

            print("[LLM] ", end="", flush=True)
            completions = await llm.astream_chat(messages=[ChatMessage(content=prompt)])
            async for completion in completions:
                print(completion.delta, end="", flush=True)
            print()


        except EOFError:
            print("\n[System] EOF received, exiting.")
            break

        except KeyboardInterrupt:
            print("\n[System] Program interrupted by user, exiting.")
            break


if __name__ == "__main__":
    import asyncio

    parser = argparse.ArgumentParser(description="LLM CLI Tool, double return to commit input, -p to read from pipe")
    parser.add_argument('-p', '--pipe', action='store_true', help="Read input from stdin (pipe)")
    args = parser.parse_args()

    asyncio.run(main(args.pipe))
