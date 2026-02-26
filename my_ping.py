import argparse
import socket
import struct
import sys
import time


def calculate_checksum(source_string):
    """
    Standard checksum calculation for ICMP packets
    """

    if len(source_string) % 2 != 0:
        source_string += b'\x00'
    
    total_sum = 0
    count = 0
    
    while count < len(source_string):
        left_byte = source_string[count]
        right_byte = source_string[count + 1]
        
        # shifts the first byte and add the second
        combined_val = (left_byte << 8) + right_byte
        total_sum = total_sum + combined_val
        count = count + 2

    while (total_sum >> 16) > 0:
        total_sum = (total_sum & 0xFFFF) + (total_sum >> 16)

    answer = ~total_sum
    answer = answer & 0xFFFF
    
    # returns in network byte order
    return socket.htons(answer)

def create_packet(id_number, sequence_number, data_size):
    """
    Packs the ICMP header and data into a binary format
    """
    icmp_type = 8 
    icmp_code = 0
    icmp_checksum = 0
    
    # BBHHH = Byte, Byte, Half word, Half word, Half fword
    header = struct.pack('BBHHH', icmp_type, icmp_code, icmp_checksum, id_number, sequence_number)
    
    # Fill payload with "a" characters to match the requested size
    payload = b'a' * data_size
    
    # calculates the checksum on header plus payload
    icmp_checksum = calculate_checksum(header + payload)
    
    # repacking the header with the real checksum
    header = struct.pack('BBHHH', icmp_type, icmp_code, icmp_checksum, id_number, sequence_number)
    
    return header + payload

def send_one_ping(target_ip, timeout, packet_id, sequence_number, data_size):
    """
    Creates a raw socket and sends one ICMP packet
    """
    
    try:
        # creates raw socket
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        
        #sets how long the socket should wait for a response later
        my_socket.settimeout(timeout)
        
        #creates the binary packet
        packet = create_packet(packet_id, sequence_number, data_size)
        
        my_socket.sendto(packet, (target_ip, 0))
        
        return my_socket
        
    except PermissionError:
        print("Error: You must run this as Administrator to use raw sockets")
        sys.exit(1)

    except Exception as e:
        print(f"Error sending packet: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Custom Python Ping Tool")
    
    #The arguments
    parser.add_argument("destination", help="The hostname or IP to ping")
    
    # The flags
    parser.add_argument("-c", "--count", type = int, help = "Stop after sending count packets")
    parser.add_argument("-i", "--wait", type = float, default=1.0, help = "Wait seconds between packets")
    parser.add_argument("-s", "--packetsize", type =int, default = 56, help = "Number of data bytes to send")
    parser.add_argument("-t", "--timeout", type = float, help = "Timeout in seconds before exiting")

    args = parser.parse_args()

    # turns hostname into an ip address
    try:
        dest_ip = socket.gethostbyname(args.destination)
    except socket.gaierror:
        print(f"Error: Could not resolve hostname '{args.destination}'")
        return

    print(f"Pinging {args.destination} [{dest_ip}] with {args.packetsize} bytes of data...")

    # testing sending one packet 
    # using pid as a simple id for the packet
    my_id = 12345 
    sock = send_one_ping(dest_ip, args.timeout, my_id, 1, args.packetsize)
    
    if sock:
        print("Da packet was sent")
        sock.close()

if __name__ == "__main__":
    main()