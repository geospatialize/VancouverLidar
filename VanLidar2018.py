import csv         # Importing the csv module for reading and writing CSV files
import os          # Importing the os module for file and directory operations
import requests    # Importing the requests module for making HTTP requests
import zipfile     # Importing the zipfile module for handling ZIP files
from tqdm import tqdm  # Importing the tqdm module for progress bars
import signal      # Importing the signal module for handling keyboard interrupts

# Input CSV file path
input_file = 'lidar-2018.csv'  # Specifying the path of the input CSV file

# Output CSV file path to store the extracted URLs
output_file = 'VanLidar2018_urls.csv'  # Specifying the path of the output CSV file to store the extracted URLs

# Directory to store the downloaded and uncompressed files
output_directory = 'VanLidar2018'  # Specifying the directory to store the downloaded and uncompressed files

# Directory to store the prj files (within the output directory)
prj_directory = os.path.join(output_directory, 'prj')  # Specifying the directory to store the prj files within the output directory

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)  # Creating the output directory if it doesn't exist, without raising an error if it already exists

# Create the prj directory within the output directory if it doesn't exist
os.makedirs(prj_directory, exist_ok=True)  # Creating the prj directory within the output directory if it doesn't exist, without raising an error if it already exists

# Open the input CSV file and read its contents
with open(input_file, 'r') as file:  # Opening the input CSV file in read mode using a context manager
    csv_reader = csv.reader(file)  # Creating a CSV reader object to read the contents of the input file
    
    # Skip the header row
    next(csv_reader)  # Skipping the header row of the input CSV file
    
    # Open the output CSV file to write the extracted URLs
    with open(output_file, 'w', newline='') as output:  # Opening the output CSV file in write mode using a context manager, with empty newline characters
        csv_writer = csv.writer(output)  # Creating a CSV writer object to write the extracted URLs to the output file
        
        # Write the header row in the output CSV file
        csv_writer.writerow(['LiDAR_URL'])  # Writing the header row with the column name 'LiDAR_URL' in the output CSV file
        
        # Initialize a counter for the number of extracted URLs
        url_count = 0  # Initializing a counter to keep track of the number of extracted URLs
        
        # Iterate over each row in the input CSV file
        for row in csv_reader:  # Iterating over each row in the input CSV file
            # Split the first column by semicolon to get the values
            values = row[0].split(';')  # Splitting the first column of the current row by semicolon to get the individual values
            
            # Extract the LiDAR URL from the second value
            lidar_url = values[1]  # Extracting the LiDAR URL from the second value in the split values
            
            # Write the URL as a row in the output CSV file
            csv_writer.writerow([lidar_url])  # Writing the LiDAR URL as a row in the output CSV file
            
            # Increment the URL counter
            url_count += 1  # Incrementing the URL counter by 1 for each extracted URL

print(f"{url_count} LiDAR URLs extracted and saved to {output_file}")  # Printing the total number of extracted URLs and the output file path

# Count the number of URLs in the output CSV file
with open(output_file, 'r') as file:  # Opening the output CSV file in read mode using a context manager
    csv_reader = csv.reader(file)  # Creating a CSV reader object to read the contents of the output file
    num_files = sum(1 for _ in csv_reader) - 1  # Counting the number of URLs in the output CSV file by summing 1 for each row, excluding the header row

# Prompt the user for a response
user_response = input(f"Do you want to proceed with downloading and extracting {num_files} files? (Y/y/N/n): ")  # Prompting the user for a response to proceed with downloading and extracting the files

if user_response.lower() in ['y', 'yes']:  # Checking if the user's response is 'y' or 'yes' (case-insensitive)
    downloaded_count = 0  # Initializing a counter for the number of downloaded ZIP files
    uncompressed_count = 0  # Initializing a counter for the number of uncompressed files
    removed_count = 0  # Initializing a counter for the number of removed ZIP files
    skipped_prj_count = 0  # Initializing a counter for the number of skipped prj files
    skipped_las_count = 0  # Initializing a counter for the number of skipped las files
    missing_prj_count = 0  # Initializing a counter for the number of missing prj files
    missing_las_count = 0  # Initializing a counter for the number of missing las files

    def download_and_extract(lidar_url):  # Defining a function to download and extract a ZIP file given a LiDAR URL
        file_name = os.path.basename(lidar_url)  # Extracting the file name from the LiDAR URL
        zip_file_path = os.path.join(output_directory, file_name)  # Constructing the path to save the downloaded ZIP file
        
        response = requests.get(lidar_url, stream=True)  # Sending a GET request to download the ZIP file, with streaming enabled
        total_size = int(response.headers.get('content-length', 0))  # Getting the total size of the ZIP file from the response headers
        block_size = 1024  # Setting the block size for downloading the file (1 KB)
        
        with open(zip_file_path, 'wb') as zip_file:  # Opening the ZIP file in write binary mode using a context manager
            for data in response.iter_content(block_size):  # Iterating over the response content in blocks
                zip_file.write(data)  # Writing each block of data to the ZIP file
        
        prj_count = 0  # Initializing a counter for the number of prj files extracted from the ZIP file
        las_count = 0  # Initializing a counter for the number of las files extracted from the ZIP file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:  # Opening the ZIP file in read mode using a context manager
            for file in zip_ref.namelist():  # Iterating over the files in the ZIP archive
                if file.endswith('.prj'):  # Checking if the file has a '.prj' extension
                    zip_ref.extract(file, prj_directory)  # Extracting the prj file to the prj directory
                    prj_count += 1  # Incrementing the prj file counter
                elif file.endswith('.las'):  # Checking if the file has a '.las' extension
                    zip_ref.extract(file, output_directory)  # Extracting the las file to the output directory
                    las_count += 1  # Incrementing the las file counter
                else:  # If the file doesn't have a '.prj' or '.las' extension
                    zip_ref.extract(file, output_directory)  # Extracting the file to the output directory
        
        os.remove(zip_file_path)  # Removing the downloaded ZIP file after extraction
        
        return file_name, "downloaded", "uncompressed", prj_count, las_count  # Returning the file name, download status, uncompress status, prj file count, and las file count

    def signal_handler(sig, frame):  # Defining a signal handler function to handle keyboard interrupts (Ctrl+C)
        print("\nProcess terminated by user.")  # Printing a message indicating that the process was terminated by the user
        print(f"Downloaded {downloaded_count} ZIP files, uncompressed {uncompressed_count} files, and removed {removed_count} ZIP files before termination.")  # Printing the counts of downloaded, uncompressed, and removed files before termination
        total_prj_files = sum(1 for file in os.listdir(prj_directory) if file.endswith('.prj'))  # Counting the total number of prj files in the prj directory
        total_las_files = sum(1 for file in os.listdir(output_directory) if file.endswith('.las'))  # Counting the total number of las files in the output directory
        print(f"There are {total_prj_files} prj files in the [...\{prj_directory}] folder and {total_las_files} las files in the [...\{output_directory}] folder")  # Printing the total counts of prj and las files in their respective directories
        os._exit(0)  # Forcing the program to exit with a status code of 0

    signal.signal(signal.SIGINT, signal_handler)  # Registering the signal handler function for the SIGINT signal (Ctrl+C)
    
    try:  # Starting a try block to handle exceptions
        # Open the output CSV file and read its contents
        with open(output_file, 'r') as file:  # Opening the output CSV file in read mode using a context manager
            csv_reader = csv.reader(file)  # Creating a CSV reader object to read the contents of the output file
            
            # Skip the header row
            next(csv_reader)  # Skipping the header row of the output CSV file
            
            print("Cross-checking prj and las files to see how many already exist...")  # Printing a message indicating the start of the cross-checking process
            
            # Perform cross-check for prj and las files
            for row in csv_reader:  # Iterating over each row in the output CSV file
                lidar_url = row[0]  # Extracting the LiDAR URL from the current row
                file_name = os.path.basename(lidar_url)  # Extracting the file name from the LiDAR URL
                if os.path.exists(os.path.join(prj_directory, file_name.replace('.zip', '.prj'))):  # Checking if the corresponding prj file already exists in the prj directory
                    skipped_prj_count += 1  # Incrementing the skipped prj file counter
                else:  # If the prj file doesn't exist
                    missing_prj_count += 1  # Incrementing the missing prj file counter
                if os.path.exists(os.path.join(output_directory, file_name.replace('.zip', '.las'))):  # Checking if the corresponding las file already exists in the output directory
                    skipped_las_count += 1  # Incrementing the skipped las file counter
                else:  # If the las file doesn't exist
                    missing_las_count += 1  # Incrementing the missing las file counter
            
            print(f"Cross-checking VanLidar2018_urls to prj and las folders Completed.")  # Printing a message indicating the completion of the cross-checking process
            print(f"{skipped_prj_count} prj files and {skipped_las_count} las files already exist.")  # Printing the counts of skipped prj and las files
            print(f"{missing_prj_count} prj files and {missing_las_count} las files are missing.")  # Printing the counts of missing prj and las files
            print(f"Initializing Downloading Process...")  # Printing a message indicating the start of the downloading process
            
            # Create a progress bar for the overall process
            progress_bar = tqdm(total=num_files, unit='file', desc='Overall Progress', leave=False)  # Creating a progress bar using tqdm to track the overall progress
            
            # Reset the file pointer to the beginning of the CSV file
            file.seek(0)  # Resetting the file pointer to the beginning of the output CSV file
            next(csv_reader)  # Skipping the header row again
            
            # Iterate over each row in the CSV file
            for row in csv_reader:  # Iterating over each row in the output CSV file
                lidar_url = row[0]  # Extracting the LiDAR URL from the current row
                file_name = os.path.basename(lidar_url)  # Extracting the file name from the LiDAR URL
                if not os.path.exists(os.path.join(prj_directory, file_name.replace('.zip', '.prj'))) or not os.path.exists(os.path.join(output_directory, file_name.replace('.zip', '.las'))):  # Checking if either the prj or las file doesn't exist
                    file_name, download_status, uncompress_status, prj_count, las_count = download_and_extract(lidar_url)  # Calling the download_and_extract function to download and extract the ZIP file
                    if download_status == "downloaded":  # Checking if the ZIP file was successfully downloaded
                        downloaded_count += 1  # Incrementing the downloaded ZIP file counter
                    if uncompress_status == "uncompressed":  # Checking if the ZIP file was successfully uncompressed
                        uncompressed_count += 1  # Incrementing the uncompressed file counter
                        removed_count += 1  # Incrementing the removed ZIP file counter
                
                # Update the progress bar with the counts after the ZIP file is removed
                progress_bar.set_postfix_str(f"{downloaded_count} ZIP files Downloaded, {uncompressed_count} files Uncompressed, {removed_count} ZIP files Removed")  # Updating the progress bar with the current counts of downloaded, uncompressed, and removed files
                progress_bar.update(1)  # Updating the progress bar by 1 unit
        
        progress_bar.close()  # Closing the progress bar after all files have been processed
        
        print(f"Downloaded {downloaded_count} ZIP files, uncompressed {uncompressed_count} files, and removed {removed_count} ZIP files.")  # Printing the final counts of downloaded, uncompressed, and removed files
        total_prj_files = sum(1 for file in os.listdir(prj_directory) if file.endswith('.prj'))  # Counting the total number of prj files in the prj directory
        total_las_files = sum(1 for file in os.listdir(output_directory) if file.endswith('.las'))  # Counting the total number of las files in the output directory
        print(f"There are {total_prj_files} prj files in the [...\{prj_directory}] folder and {total_las_files} las files in the [...\{output_directory}] folder")  # Printing the total counts of prj and las files in their respective directories
    except Exception as e:  # Catching any exceptions that occur during the execution
        print(f"An error occurred: {str(e)}")  # Printing the error message
        print(f"Downloaded {downloaded_count} ZIP files, uncompressed {uncompressed_count} files, and removed {removed_count} ZIP files before the error.")  # Printing the counts of downloaded, uncompressed, and removed files before the error occurred
        total_prj_files = sum(1 for file in os.listdir(prj_directory) if file.endswith('.prj'))  # Counting the total number of prj files in the prj directory
        total_las_files = sum(1 for file in os.listdir(output_directory) if file.endswith('.las'))  # Counting the total number of las files in the output directory
        print(f"There are {total_prj_files} prj files in the [...\{prj_directory}] folder and {total_las_files} las files in the [...\{output_directory}] folder")  # Printing the total counts of prj and las files in their respective directories
else:                                                                                                                                       
    print("Skipping the download and extraction process.")  # Printing a message indicating that the download and extraction process is being skipped
