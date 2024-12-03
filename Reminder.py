#!/usr/bin/env python3

import time
import os
from colorama import Fore, Style

def main():
    start_time = time.time()
    # Set the reminder interval to 6 hours (6 * 60 minutes * 60 seconds)
    reminder_interval = 6 * 60 * 60

    # Print a message indicating the reminder is set, showing the interval in hours
    print(f"{Fore.RED}Задолбалка {Style.RESET_ALL}поставлена. Напомню через {reminder_interval / 3600} часов.")

    def send_notification():
        os.system('notify-send "Напоминание" "Пора сделать перерыв! Отвлекись от компьютера."')


    # Start an infinite loop to check if the reminder time has passed
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time >= reminder_interval:
            send_notification()
            start_time = time.time()
        time.sleep(60)

if __name__ == "__main__":
    main()
