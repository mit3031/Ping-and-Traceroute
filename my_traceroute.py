import argparse
import socket
import sys
import time

def calculate_checksum(source_string): #copied from ping
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


def send_probe(dest_ip, port, ttl):
    """
    Sends a simple UDP probe with a specific TTL.
    """
    try:
        # creates UDP socket
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        
        # Sets the TTL 
        # Tells the router to drop the packet after ttl hops
        send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
        
        # this just sends a dummy message
        send_sock.sendto(b"", (dest_ip, port))
        
        return send_sock
    except Exception as e:
        print(f"Error sending probe: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Custom Python Traceroute Tool")
    
    #arguments
    parser.add_argument("destination", help="The destination hostname or IP")
    
    #flags
    parser.add_argument("-n", action = "store_true", help = "Print hop addresses numerically")
    parser.add_argument("-q", "--nqueries", type=int, default = 3, help = "Number of probes per TTL")
    parser.add_argument("-S", "--summary", action = "store_true", help = "Print summary of unanswered probes")

    args = parser.parse_args()

    # turns hostname into an ip address
    try:
        dest_ip = socket.gethostbyname(args.destination)
    except socket.gaierror:
        print(f"Error: Could not resolve {args.destination}")
        return

    print(f"my_traceroute to {args.destination} ({dest_ip}), 30 hops max")

    # test for socket setup
    try:
        
        recv_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        recv_sock.settimeout(2.0)
        
        # Test sending a probe with TTL 1
        test_port = 33434
        sender = send_probe(dest_ip, test_port, 1)
        
        if sender:
            print("UDP probe sent and ICMP listener ready")
            sender.close()
            recv_sock.close()

    except PermissionError:
        print("Error: Traceroute requires Administrator privileges for raw sockets")
        sys.exit(1)

if __name__ == "__main__":
    main()