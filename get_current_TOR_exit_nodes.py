import requests
from bs4 import BeautifulSoup
import re

def get_latest_exit_list_url(base_url):
    # Fetch the content of the index page
    response = requests.get(base_url)
    response.raise_for_status()  # Raise an error for bad responses

    # Parse the page content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the latest exit list link by using regex
    latest_file_link = soup.find('a', href=re.compile(r'\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}'))
    if latest_file_link and latest_file_link['href']:
        return "https://collector.torproject.org/recent/exit-lists/" + latest_file_link['href']
    else:
        raise Exception("Could not find the latest exit list file.")

def download_exit_list(file_url):
    # Download the latest exit list file
    response = requests.get(file_url)
    response.raise_for_status()  # Raise an error for bad responses
    return response.text, file_url.split('/')[-1]  # Return content and the filename

def extract_ipv4_addresses(file_content):
    # Find all lines that contain 'ExitAddress' and extract the IPs
    ipv4_addresses = set()  # Use a set to avoid duplicates
    lines = file_content.splitlines()
    for line in lines:
        if line.startswith('ExitAddress'):
            # Split the line and get the second part as the IP address
            parts = line.split()
            if len(parts) >= 2:
                ipv4_addresses.add(parts[1])  # Add the IP address to the set
    return list(ipv4_addresses)  # Convert the set back to a list

def save_to_file(ipv4_addresses, output_filename):
    # Save the list of IP addresses to a file
    with open(output_filename, 'w') as file:
        for ipv4 in ipv4_addresses:
            file.write(f"{ipv4}\n")

def main():
    base_url = 'https://collector.torproject.org/recent/exit-lists/?C=M;O=D'
    
    try:
        latest_file_url = get_latest_exit_list_url(base_url)
        print(f'Downloading exit list from: {latest_file_url}')
        
        file_content, current_filename = download_exit_list(latest_file_url)

        ipv4_addresses = extract_ipv4_addresses(file_content)

        # Create the output filename with the current file name prepended
        output_filename = f"{current_filename}_current_tor_exit_nodes.txt"
        save_to_file(ipv4_addresses, output_filename)
        print(f'Saved {len(ipv4_addresses)} unique IP addresses to {output_filename}')
    
    except Exception as e:
        print(f'An error occurred: {e}')

if __name__ == "__main__":
    main()
