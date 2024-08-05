import argparse
import subprocess
from itertools import product
import os

def create_char_dict(file_path):
    char_dict = {}

    # Open the file with UTF-8 encoding
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # Strip any surrounding whitespace, including newline characters
            line = line.strip()
            if not line:
                continue

            # The first character is the key
            key = ord(line[0])

            # The rest of the characters are the alternative chars
            alt_chars = line[1:]

            # Create the list of ord values for the alternative chars
            ord_values = [ord(char) for char in alt_chars]

            # Store in the dictionary
            char_dict[key] = ord_values

    return char_dict

def generate_permutations_lazy(url, char_dict):
    # Create a list of lists where each list contains the ord values of the char and its alternatives
    substitution_lists = []
    for char in url:
        char_ord = ord(char)
        # Include the character itself and its alternatives if present in the dictionary
        substitutions = [char_ord] + char_dict.get(char_ord, [])
        substitution_lists.append(substitutions)

    # Generate all combinations of the substitutions lazily
    for combination in product(*substitution_lists):
        yield ''.join(chr(c) for c in combination)

def ping_host(host):
    try:
        # Use the '-n' option for Windows and '-c' for Unix-based systems
        command = ['ping', '-c', '1', host] if not os.name == 'nt' else ['ping', '-n', '1', host]
        output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # If the host is found, ping will return 0
        return output.returncode == 0
    except Exception as e:
        print(f"Error pinging host {host}: {e}")
        return False

def main(args):
    char_dict = create_char_dict(args.file_path)
    url = args.url
    N = args.N
    output_file = args.output_file
    if output_file == 'URL_tested.txt':
        output_file = url+'_tested.txt'
    found_hosts = []

    permutations = generate_permutations_lazy(url, char_dict)

    # Ping each permutation
    try:
        for i, perm in enumerate(permutations):
            if ping_host(perm):
                found_hosts.append(perm)

            if (i + 1) % N == 0:
                print(f"{i + 1} permutations tested. Do you want to continue? (yes/no)")
                answer = input().strip().lower()
                if answer != 'yes':
                    break

    except KeyboardInterrupt:
        print("Process interrupted by user")

    print(f"Number of hosts found: {len(found_hosts)}")

    # Save found hosts to a file if output file is specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            for host in found_hosts:
                f.write(f"{host}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate permutations and ping hosts.")
    
    # Mandatory arguments
    parser.add_argument('-u', '--url', required=True, help='The URL to generate permutations for.')
    parser.add_argument('-N', type=int, required=True, help='Number of permutations before asking to continue.')
    
    # Optional arguments with default values
    parser.add_argument('-o', '--output_file', default='URL_tested.txt', help='Name of the output file to save found hosts.')
    parser.add_argument('-i', '--file_path', default='chars.txt', help='Path to the file containing character alternatives.')

    args = parser.parse_args()
    main(args)
