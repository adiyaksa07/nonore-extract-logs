import os
import platform
import sys
import time
import tldextract
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def clear_console():
    """Clear the console based on the operating system."""
    os_system = platform.system()
    if os_system == "Windows":
        os.system('cls')
    else:  # For Unix/Linux/MacOS
        os.system('clear')

def logo_nonore():
    logo = r"""
     _   _  ___  _   _  ____  _____  ______ 
    | \ | |/ _ \| \ | |/ __ \|  __ \|  ____|
    |  \| | | | |  \| | |  | | |__) | |__   
    | .  | | | | .  | |  | |  _  /|  __|  
    | |\  | |_| | |\  | |__| | | \ \| |____ 
    |_| \_|\___/|_| \_|\____/|_|  \_\______|
    """
    print(f"\n{Fore.RED}--------------------------------{Style.RESET_ALL}")
    print(Fore.RED + logo + Style.RESET_ALL)
    print(f"{Fore.RED} Author : Adiyaksa {Style.RESET_ALL}")
    print(f"{Fore.RED}--------------------------------{Style.RESET_ALL}")

def extract_credentials(input_files, output_file, search_pattern, include_url, exclude_https, search_port=None):
    try:
        os.makedirs("result", exist_ok=True)
        output_path = os.path.join("result", output_file)

        print(f"{Fore.CYAN}[INFO] Reading input files...")

        start_time = time.time()

        credentials_set = set()
        credentials_found = 0

        with open(output_path, 'w', encoding='utf-8') as outfile:
            for input_file in input_files:
                try:
                    with open(input_file, 'r', encoding='utf-8') as infile:
                        for line in infile:
                            # Skip lines that start with unwanted prefixes
                            if exclude_https and line.lstrip().startswith(("https", "http", "android", "//")):
                                continue
                            
                            if not exclude_https and (line.startswith("http://") or line.startswith("https://")):
                                line = line.split("://", 1)[-1]

                            # Extract TLD using tldextract
                            extracted = tldextract.extract(line)
                            tld = '.' + extracted.suffix if extracted.suffix else ''
                            domain = extracted.domain + tld if extracted.domain else ''

                            # Check if the line matches the search pattern and optionally the port
                            if search_pattern and search_pattern not in domain:
                                continue

                            if search_port and f":{search_port}:" not in line:
                                continue
     
                            parts = line.strip().split(':')

                            port = ''

                            if len(parts) == 3:
                                url = parts[0].strip()
                                username = parts[1].strip()
                                password = parts[2].strip()

                            elif len(parts) == 4:
                                url = parts[0].strip()
                                port = parts[1].strip()
                                username = parts[2].strip()
                                password = parts[3].strip()
                            
                            else:
                                credential = line.strip()
                            
                             # Filter out unwanted keywords in username or password if exclude_https is True
                            if exclude_https and any(unwanted in username or unwanted in password for unwanted in ['https', 'http', 'android', '//']):
                                continue
                            if include_url:
                                credential = f'{url}:{port}:{username}:{password}' if search_port or len(str(port)) >= 2 else f'{url}:{username}:{password}'
                            else:
                                credential = f'{username}:{password}'

                            # Ensure the credential is not already added
                            if credential not in credentials_set:
                                credentials_set.add(credential)
                                outfile.write(credential + '\n')
                                print(f"{Fore.GREEN}[+] Found: {credential}")
                                credentials_found += 1

                except FileNotFoundError:
                    print(f"{Fore.RED}[ERROR] File '{input_file}' not found.")
                except IOError as e:
                    print(f"{Fore.RED}[ERROR] I/O error reading '{input_file}'. Details: {e}")
                except UnicodeDecodeError as e:
                    print(f"{Fore.RED}[ERROR] Unicode decoding error reading '{input_file}'. Details: {e}")

        end_time = time.time()
        time_taken = end_time - start_time

        print(f"{Fore.YELLOW}[INFO] Processing complete! {credentials_found} credentials extracted.")
        print(f"{Fore.YELLOW}[INFO] Credentials successfully extracted and written to '{output_path}'.")
        print(f"{Fore.YELLOW}[INFO] Time taken for extraction: {time_taken:.2f} seconds.")

    except IOError as e:
        print(f"{Fore.RED}[ERROR] I/O error. Details: {e}")

def get_user_input():
    """
    Prompt the user for input file names, output file name, and search pattern.
    The user can choose to search by TLD, URL, text, port, or a combination.
    """
    clear_console()
    logo_nonore()

    def input_with_validation(prompt):
        value = input(prompt).strip()
        if not value:
            print(f"{Fore.RED}[ERROR] Input cannot be empty!")
            return input_with_validation(prompt)
        return value

    input_filenames = input_with_validation(Fore.MAGENTA + "Enter input file names (can be combined, e.g., data.txt data2.txt): " + Style.RESET_ALL).split()
    output_filename = input_with_validation(Fore.MAGENTA + "Enter output file name (e.g., credentials.txt): " + Style.RESET_ALL)

    search_type = input_with_validation(Fore.MAGENTA + "Search by (1) TLD, (2) URL, (3) Text, or (4) Port? (1/2/3/4): " + Style.RESET_ALL)
    
    if search_type == '1':
        search_pattern = input_with_validation(Fore.MAGENTA + "Enter the TLD to search for (e.g., .com): " + Style.RESET_ALL)
        search_port = None
    elif search_type == '2':
        search_pattern = input_with_validation(Fore.MAGENTA + "Enter the URL to search for (e.g., google.com): " + Style.RESET_ALL)
        search_port = None
    elif search_type == '3':
        search_pattern = input_with_validation(Fore.MAGENTA + "Enter the text to search for (e.g., netflix): " + Style.RESET_ALL)
        search_port = None
    elif search_type == '4':
        search_port = input_with_validation(Fore.MAGENTA + "Enter the port to search for (e.g., 2083): " + Style.RESET_ALL)
        search_pattern = ""
    else:
        print(f"{Fore.RED}[INFO] Invalid option. Defaulting to TLD.")
        search_pattern = '.com'
        search_port = None

    include_url = input_with_validation(Fore.MAGENTA + "Include URLs in the output? (y/n): " + Style.RESET_ALL).lower() == 'y'
    exclude_https = input_with_validation(Fore.MAGENTA + "Filter out https, http, and android data? (y/n): " + Style.RESET_ALL).lower() == 'y'
    
    return input_filenames, output_filename, search_pattern, include_url, exclude_https, search_port

def handle_args():
    """
    Handle command line arguments.
    """
    if len(sys.argv) >= 5:
        input_filenames = sys.argv[1].split()
        output_filename = sys.argv[3]
        search_pattern = sys.argv[4]
        include_url = True if len(sys.argv) > 5 and sys.argv[5].lower() == 'y' else False
        exclude_https = True if len(sys.argv) > 6 and sys.argv[6].lower() == 'y' else False
        search_port = sys.argv[7] if len(sys.argv) > 7 else None

        extract_credentials(input_filenames, output_filename, search_pattern, include_url, exclude_https, search_port)
    else:
        print(f"{Fore.RED}[ERROR] Incomplete arguments. Example usage: script.py \"data.txt data2.txt\" output.txt text [y/n] [y/n] [port]")

try:
    if len(sys.argv) > 1:
        handle_args()
    else:
        input_filenames, output_filename, search_pattern, include_url, exclude_https, search_port = get_user_input()

        extract_credentials(input_filenames, output_filename, search_pattern, include_url, exclude_https, search_port)

except KeyboardInterrupt:
    print(f"{Fore.RED}\n[INFO] Process interrupted by user (Ctrl + C).")
