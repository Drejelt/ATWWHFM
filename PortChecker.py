import socket
from time import sleep
from colorama import Fore, Style  # pip install colorama

def port_check(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)  # Timeout of 2 seconds for the connection attempt.
    try:
        s.connect((host, port))
        return True
    except:
        return False
    finally:
        s.close()

while True:
    try:
        host = input(f'Enter the target {Fore.YELLOW}IP address{Style.RESET_ALL}: ')
        port = int(input(f'Enter the target {Fore.GREEN}Port{Style.RESET_ALL}: '))

        if port_check(host, port):
            print(f"Port {Fore.MAGENTA}{port}{Style.RESET_ALL} on {Fore.YELLOW}{host}{Style.RESET_ALL} is {Fore.GREEN}open{Style.RESET_ALL}.")
            break
        else:
            print(f"Port {Fore.MAGENTA}{port}{Style.RESET_ALL} on {Fore.YELLOW}{host}{Style.RESET_ALL} is {Fore.RED}closed{Style.RESET_ALL}.")
            break
    except ValueError:
        print(f"{Fore.RED}Invalid port number. Please enter a valid integer.{Style.RESET_ALL}")
        sleep(0.1)

