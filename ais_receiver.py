import requests
import argparse
from pyais.stream import UDPReceiver
from enum import Enum

def convert_enum_to_string(data: dict):
    converted_data = {}
    for key, value in data.items():
        if isinstance(value, Enum):
            value = value.name
        converted_data[key] = value
    return converted_data

def read_token_from_file(token_file):
    with open(token_file, "r") as file:
        return file.read().strip()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP Receiver and POST Sender")
    parser.add_argument("--host", type=str, default="localhost", help="UDP server host")
    parser.add_argument("--port", type=int, default=10110, help="UDP server port")
    parser.add_argument("--endpoint", type=str, default="svais.jbl.mooo.com/api/coords/coords", help="API endpoint")
    parser.add_argument("--protocol", choices=["http", "https"], default="https", help="HTTP protocol")
    parser.add_argument("--token", type=str, default="token", help="Authentication token")
    parser.add_argument("--token-file", type=str, help="File containing the authentication token")
    args = parser.parse_args()

    if args.token and args.token_file:
        print("Error: Please provide either a token or a token file, not both.")
        exit(1)

    if args.token_file:
        auth_token = read_token_from_file(args.token_file)
    else:
        auth_token = args.token

    url = f"{args.protocol}://{args.endpoint}"

    headers = {
        'Authorization': 'Bearer ' + auth_token,
        'Content-Type': 'application/json'
    }

    for msg in UDPReceiver(args.host, port=args.port):
        msg = msg.encode('utf-8')
        msg = {
            'nmea': msg
        }
        response = requests.post(url, json=msg, headers=headers)
        if response.status_code == 200:
            print('POST request was successful!')
        else:
            print(f'POST request failed with status code: {response.status_code}')
