import os
import requests
import asyncio
import aiohttp
import re


print("""
 __                               _  __
/\ \ \_   _ _ __ ___/\   /\___ _ __(_)/ _|_   _
/  \/ / | | | '_ ` _ \ \ / / _ \ '__| | |_| | | |
/ /\  /| |_| | | | | | \ V /  __/ |  | |  _| |_| |
\_\ \/  \__,_|_| |_| |_|\_/ \___|_|  |_|_|  \__, |
                                            |___/
\n By TheRealinvisible
""")
      
api_key = input("Enter your NumVerify API key: ")
numbers_file = input("Enter the name of the numbers.txt file: ")

current_dir = os.path.dirname(os.path.abspath(__file__))
numbers_file_path = os.path.join(current_dir, numbers_file)

valid_numbers_dir = os.path.join(current_dir, "valid_numbers")
invalid_numbers_dir = os.path.join(current_dir, "invalid_numbers")
carrier_info_dir = os.path.join(current_dir, "carrier_info")
landline_numbers_dir = os.path.join(current_dir, "landline_numbers")

os.makedirs(valid_numbers_dir, exist_ok=True)
os.makedirs(invalid_numbers_dir, exist_ok=True)
os.makedirs(carrier_info_dir, exist_ok=True)
os.makedirs(landline_numbers_dir, exist_ok=True)

async def validate_number(session, number):
    url = f"http://apilayer.net/api/validate?access_key={api_key}&number={number}&country_code=&format=1"
    async with session.get(url) as response:
        data = await response.json()
        return number, data.get("valid", False), data.get("carrier", ""), data.get("line_type", "")

async def main():
    numbers = []
    with open(numbers_file_path, "r") as file:
        numbers = [line.strip() for line in file]

    async with aiohttp.ClientSession() as session:
        tasks = [validate_number(session, number) for number in numbers]
        results = await asyncio.gather(*tasks)

    carrier_numbers = {}
    carrier_folders = {}

    for number, is_valid, carrier, line_type in results:
        if is_valid:
            print(f"{number} is valid")
            if line_type == "landline" or not carrier:
                with open(os.path.join(landline_numbers_dir, "landline_numbers.txt"), "a") as landline_file:
                    landline_file.write(number + "\n")
            else:
                if carrier in carrier_numbers:
                    carrier_numbers[carrier].append(number)
                else:
                    carrier_numbers[carrier] = [number]

                modified_carrier = re.sub(r'[<>:"/\\|?*]', '_', carrier)

                if modified_carrier not in carrier_folders:
                    carrier_folder = os.path.join(carrier_info_dir, modified_carrier)
                    os.makedirs(carrier_folder, exist_ok=True)
                    carrier_folders[modified_carrier] = carrier_folder

                with open(os.path.join(carrier_folders[modified_carrier], f"{modified_carrier}_numbers.txt"), "a") as carrier_file:
                    carrier_file.write(number + "\n")

                    with open(os.path.join(valid_numbers_dir, "valid_numbers.txt"), "a") as valid_file:
                        valid_file.write(number + "\n")
        else:
            print(f"{number} is invalid")

            with open(os.path.join(invalid_numbers_dir, "invalid_numbers.txt"), "a") as invalid_file:
                invalid_file.write(number + "\n")

    for carrier, numbers in carrier_numbers.items():

        modified_carrier = re.sub(r'[<>:"/\\|?*]', '_', carrier)


        with open(os.path.join(carrier_folders[modified_carrier], f"{modified_carrier}_numbers.txt"), "a") as carrier_file:
            carrier_file.write("\n".join(numbers))

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
