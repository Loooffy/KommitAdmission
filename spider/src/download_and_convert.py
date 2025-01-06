import os
import requests
from markitdown import MarkItDown
from urllib.parse import urlparse
from datetime import datetime
import concurrent.futures
import threading

# Add a thread-safe print function
print_lock = threading.Lock()
def safe_print(message):
    with print_lock:
        print(message)

class MarkdownConverter:
    def convert_markdown(self, input_file_name):
        md = MarkItDown()
        result = md.convert(input_file_name)
        return result

def convert_html_to_markdown(url):
    """
    Convert HTML to markdown using the local NestJS service
    """
    try:
        response = requests.post(
            'http://localhost:3000/convert',
            json={'url': url}
        )
        response.raise_for_status()
        return response.json()['markdown']
    except requests.RequestException as e:
        raise Exception(f"Failed to convert using local service: {str(e)}")

def process_single_link(link, output_dir):
    """
    Process a single link - download and convert to markdown
    """
    try:
        if link.lower().endswith('.pdf'):
            # Handle PDFs using MarkItDown
            response = requests.get(link, stream=True)
            response.raise_for_status()
            
            temp_pdf_path = os.path.join(output_dir, f"temp_{threading.get_ident()}.pdf")
            
            with open(temp_pdf_path, 'wb') as pdf_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        pdf_file.write(chunk)
            
            converter = MarkdownConverter()
            markdown_content = converter.convert_markdown(temp_pdf_path)
            
            parsed_url = urlparse(link)
            filename = f"{parsed_url.netloc.replace('.', '_')}_{parsed_url.path.replace('/', '_')}.md"
            file_path = os.path.join(output_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as md_file:
                md_file.write(markdown_content.text_content)
            
            os.remove(temp_pdf_path)
            safe_print(f"Downloaded and converted PDF: {link}")
            
        else:
            # Handle HTML using local NestJS service
            markdown_content = convert_html_to_markdown(link)
            
            parsed_url = urlparse(link)
            filename = f"{parsed_url.netloc.replace('.', '_')}_{parsed_url.path.replace('/', '_')}.md"
            file_path = os.path.join(output_dir, filename)

            with open(file_path, 'w', encoding='utf-8') as md_file:
                md_file.write(markdown_content)

            safe_print(f"Downloaded and converted HTML: {link}")
        
        return True

    except Exception as e:
        safe_print(f"Failed to process {link}: {e}")
        return False

def download_and_convert_links(file_path, output_dir, max_workers=5):
    """
    Download and convert links using multiple threads
    """
    os.makedirs(output_dir, exist_ok=True)

    with open(file_path, 'r') as f:
        links = [line.strip() for line in f]

    # Use ThreadPoolExecutor for parallel processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks and collect futures
        future_to_link = {
            executor.submit(process_single_link, link, output_dir): link 
            for link in links
        }

        # Process completed tasks as they finish
        completed = 0
        total = len(links)
        for future in concurrent.futures.as_completed(future_to_link):
            link = future_to_link[future]
            completed += 1
            safe_print(f"Progress: {completed}/{total} links processed")

def merge_markdown_files(directory_path, output_filename):
    """
    Merge all markdown files in the given directory into a single file
    """
    # Get all markdown files in the directory
    md_files = [f for f in os.listdir(directory_path) if f.endswith('.md')]
    
    # Create the merged file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    merged_filename = f"{output_filename}_{timestamp}.md"
    merged_filepath = os.path.join(directory_path, merged_filename)
    
    with open(merged_filepath, 'w', encoding='utf-8') as outfile:
        # Write header
        outfile.write(f"# Merged Markdown Documents\n")
        outfile.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        
        # Process each markdown file
        for md_file in sorted(md_files):
            file_path = os.path.join(directory_path, md_file)
            
            # Add file separator and name
            outfile.write(f"\n---\n")
            outfile.write(f"## Source: {md_file}\n\n")
            
            # Copy content
            with open(file_path, 'r', encoding='utf-8') as infile:
                outfile.write(infile.read())
            outfile.write("\n")
    
    print(f"Merged {len(md_files)} files into {merged_filename}")
    return merged_filepath

if __name__ == "__main__":
    school_name = input("Enter the school name: ")
    input_file_path = os.path.join(f'../data/{school_name}', 'links.txt')
    output_directory = os.path.join(f'../data/{school_name}', f'{school_name}_markdown')

    # Download and convert files
    download_and_convert_links(input_file_path, output_directory)
    
    # Merge all markdown files
    merged_file = merge_markdown_files(output_directory, f"{school_name}_merged")
    print(f"All documents have been merged into: {merged_file}") 