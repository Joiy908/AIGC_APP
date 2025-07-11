import sys
import platform


if __name__ == '__main__':


    for line in sys.stdin:
        print('From stdin: ', line.strip())


    def win_read_keyboard_input():
        import msvcrt
        buffer = ''
        while True:
            ch = msvcrt.getwch()
            if ch == '\r':
                print()
                return buffer
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

    usr_in = win_read_keyboard_input_multiline()
    print('user in:', usr_in)
