import socket
import json
from ais_decoder import parse_ais_messages

def quotify(x):
    if isinstance(x, str):
        return '"' + str(x) + '"'
    else:
        return str(x)


def save_to_file(data):
    with open('ais.json', 'r') as file:
        file_data = json.loads(file.read())
    file_data.append(data)
    with open('ais.json', 'w') as file:
        file.write(json.dumps(file_data, indent=4))

def main():
    # Define the host and port to listen on
    host = "localhost"
    port = 10110

    # Create a UDP socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        # Bind the socket to the host and port
        server_socket.bind((host, port))

        print(f"Listening for UDP packets on {host}:{port}...")

        while True:
            # Receive data from the client
            print()
            for raw, parsed, bogon in parse_ais_messages(server_socket, False, True, 0):
                if not bogon:
                    print(raw)
                    data_json = {
                        x[0].name: quotify(x[1]) for x in parsed
                    }
                    save_to_file(data_json)
            # print(f"Received data from {client_address}: {data.decode('utf-8')}")


if __name__ == "__main__":
    main()
