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
    parser.add_argument("--email", type=str, help="Authentication token")
    args = parser.parse_args()

    if not args.email:
        print('Please provide a valid email.')
        exit()
        
    url = f"{args.protocol}://{args.endpoint}"


    for msg in UDPReceiver(args.host, port=args.port):
        msg = msg.raw.decode('utf-8')
        msg = {
            'email': args.email,
            'nmea': msg
        }
        response = requests.post(url, json=msg)
        if response.status_code == 200:
            print(f'Server_response: {response._content}')
        else:
            print(f'POST request failed with status code: {response.status_code}')
