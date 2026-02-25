import argparse
import sys

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

    print(f"Pinging {args.destination} with {args.packetsize} bytes of data...")

if __name__ == "__main__":
    main()