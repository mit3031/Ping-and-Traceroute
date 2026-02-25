import argparse

def main():
    parser = argparse.ArgumentParser(description="Custom Python Traceroute Tool")
    
    #arguments
    parser.add_argument("destination", help="The destination hostname or IP")
    
    #flags
    parser.add_argument("-n", action = "store_true", help = "Print hop addresses numerically")
    parser.add_argument("-q", "--nqueries", type=int, default = 3, help = "Number of probes per TTL")
    parser.add_argument("-S", "--summary", action = "store_true", help = "Print summary of unanswered probes")

    args = parser.parse_args()

    print(f"Traceroute to {args.destination} (max 30 hops)...")

if __name__ == "__main__":
    main()