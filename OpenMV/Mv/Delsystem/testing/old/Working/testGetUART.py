# from fpioa_manager import fm
# from machine import UART
# from board import board_info

# fm.register(board_info.PIN11, fm.fpioa.UART2_RX, force=True)
# uart_B = UART(UART.UART2, 115200, 8, 0, 0, timeout=1000, read_buf_len=4096)

# while True:
#     startObserving = uart_B.read()
#     print(startObserving)


from fpioa_manager import fm
from machine import UART
from board import board_info

fm.register (board_info.PIN15, fm.fpioa.UART1_TX)
fm.register (board_info.PIN17, fm.fpioa.UART1_RX)
fm.register (board_info.PIN9, fm.fpioa.UART2_TX)
fm.register (board_info.PIN10, fm.fpioa.UART2_RX)

uart_A = UART (UART.UART1, 115200, 8, None, 1, timeout = 1000, read_buf_len = 4096)
uart_B = UART (UART.UART2, 115200, 8, None, 1, timeout = 1000, read_buf_len = 4096)

while True:
    read_data = uart_B.read()
    print(read_data)
    if read_data is not None:
        read_str = read_data.decode('utf-8')
        print(read_str)
