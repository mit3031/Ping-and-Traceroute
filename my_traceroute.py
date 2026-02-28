import argparse
import socket
import sys
import time
import struct

def calculate_checksum(source_string): #copied from ping
    """
    Checksum calculation for ICMP packets
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
    Sends a simple UDP probe with a specific TTL
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
    
def receive_result(recv_sock, timeout):
    """
    Waits for an ICMP response and returns the senders IP and ICMP type
    """
    start_time = time.time()
    while True:
        time_left = timeout - (time.time() - start_time)
        if time_left <= 0:
            return None, None, 0

        try:
            packet, addr = recv_sock.recvfrom(1024)
            time_received = time.time()
            
            # ICMP header is after the 20 byte IP header
            icmp_header = packet[20:28]
            icmp_type, icmp_code, checksum, p_id, seq = struct.unpack("BBHHH", icmp_header)
            
            rtt = (time_received - start_time) * 1000
            return addr[0], icmp_type, rtt
            
        except socket.timeout:
            return None, None, 0

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
        
        # start at ttl 1 and go up to 30
        for ttl in range(1, 31):
            # print the hop number
            print(f"{ttl:2}  ", end="", flush=True)
            
            curr_addr = None
            probe_times = []
            lost_count = 0
            reached_end = False

            # send the amount of probes requested by -q flag
            for i in range(args.nqueries):
                # use a common starting port for traceroute
                send_sock = send_probe(dest_ip, 33434 + i, ttl)
                
                # waits for the icmp response
                addr, icmp_type, rtt = receive_result(recv_sock, 2.0)
                
                if addr:
                    curr_addr = addr
                    probe_times.append(f"{rtt:.3f} ms")

                    # if the type is 3 or the addr is our dest we are done
                    if addr == dest_ip or icmp_type == 3:
                        reached_end = True
                else:
                    probe_times.append("*")
                    lost_count += 1
                
                if send_sock:
                    send_sock.close()

            # print the address info for this hop
            if curr_addr:
                display_name = curr_addr
                # only try to get the hostname if -n is not a set
                if not args.n:
                    try:
                        host_info = socket.gethostbyaddr(curr_addr)
                        display_name = f"{host_info[0]} ({curr_addr})"
                    except socket.herror:
                        display_name = curr_addr
                
                print(f"{display_name}  ", end="")
            
            # print all the probe results
            print("  ".join(probe_times), end = "")

            # if the -s flag is used we show the lost probe count
            if args.summary:
                print(f"  [{lost_count} probes lost]", end="")
            
            print() # move to the next line

            if reached_end:
                break

        recv_sock.close()

    except PermissionError:
        print("Error: Traceroute requires administrator privileges for raw sockets")
        sys.exit(1)

if __name__ == "__main__":
    main()