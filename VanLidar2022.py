import csv         # Importing the csv module for reading and writing CSV files
import os          # Importing the os module for file and directory operations
import requests    # Importing the requests module for making HTTP requests
import zipfile     # Importing the zipfile module for handling ZIP files
from tqdm import tqdm  # Importing the tqdm module for progress bars
import signal      # Importing the signal module for handling keyboard interrupts

# Input CSV file path
input_file = 'lidar-2022.csv'  # Specifying the path of the input CSV file

# Output CSV file path to store the extracted URLs
output_file = 'VanLidar2022_urls.csv'  # Specifying the path of the output CSV file to store the extracted URLs

# Directory to store the downloaded and uncompressed files
output_directory = 'VanLidar2022'  # Specifying the directory to store the downloaded and uncompressed files

# Directory to store the lasx files (within the output directory)
lasx_directory = os.path.join(output_directory, 'lasx')  # Specifying the directory to store the lasx files within the output directory

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)  # Creating the output directory if it doesn't exist, without raising an error if it already exists

# Create the lasx directory within the output directory if it doesn't exist
os.makedirs(lasx_directory, exist_ok=True)  # Creating the lasx directory within the output directory if it doesn't exist, without raising an error if it already exists

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
    uncompressed_las_count = 0  # Initializing a counter for the number of uncompressed las files
    uncompressed_lasx_count = 0  # Initializing a counter for the number of uncompressed lasx files
    removed_count = 0  # Initializing a counter for the number of removed ZIP files
    skipped_las_count = 0  # Initializing a counter for the number of skipped las files
    skipped_lasx_count = 0  # Initializing a counter for the number of skipped lasx files
    missing_las_count = 0  # Initializing a counter for the number of missing las files
    missing_lasx_count = 0  # Initializing a counter for the number of missing lasx files

    def download_and_extract(lidar_url):  # Defining a function to download and extract a ZIP file given a LiDAR URL
        file_name = os.path.basename(lidar_url)  # Extracting the file name from the LiDAR URL
        zip_file_path = os.path.join(output_directory, file_name)  # Constructing the path to save the downloaded ZIP file
        
        response = requests.get(lidar_url, stream=True)  # Sending a GET request to download the ZIP file, with streaming enabled
        total_size = int(response.headers.get('content-length', 0))  # Getting the total size of the ZIP file from the response headers
        block_size = 1024  # Setting the block size for downloading the file (1 KB)
        
        with open(zip_file_path, 'wb') as zip_file:  # Opening the ZIP file in write binary mode using a context manager
            for data in response.iter_content(block_size):  # Iterating over the response content in blocks
                zip_file.write(data)  # Writing each block of data to the ZIP file
        
        las_count = 0  # Initializing a counter for the number of las files extracted from the ZIP file
        lasx_count = 0  # Initializing a counter for the number of lasx files extracted from the ZIP file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:  # Opening the ZIP file in read mode using a context manager
            for file in zip_ref.namelist():  # Iterating over the files in the ZIP archive
                if file.endswith('.lasx'):  # Checking if the file has a '.lasx' extension
                    zip_ref.extract(file, lasx_directory)  # Extracting the lasx file to the lasx directory
                    lasx_count += 1  # Incrementing the lasx file counter
                else:  # If the file doesn't have a '.lasx' extension
                    zip_ref.extract(file, output_directory)  # Extracting the file to the output directory
                    las_count += 1  # Incrementing the las file counter
        
        os.remove(zip_file_path)  # Removing the downloaded ZIP file after extraction
        
        return file_name, "downloaded", "uncompressed", las_count, lasx_count  # Returning the file name, download status, uncompress status, las file count, and lasx file count

    def signal_handler(sig, frame):  # Defining a signal handler function to handle keyboard interrupts (Ctrl+C)
        print("\nProcess terminated by user.")  # Printing a message indicating that the process was terminated by the user
        print(f"Downloaded {downloaded_count} ZIP files, uncompressed {uncompressed_las_count} las files and {uncompressed_lasx_count} lasx files, and removed {removed_count} ZIP files before termination.")  # Printing the counts of downloaded, uncompressed, and removed files before termination
        total_las_files = sum(1 for file in os.listdir(output_directory) if file.endswith('.las'))  # Counting the total number of las files in the output directory
        total_lasx_files = sum(1 for file in os.listdir(lasx_directory) if file.endswith('.lasx'))  # Counting the total number of lasx files in the lasx directory
        print(f"There are {total_las_files} las files in the [...\{output_directory}] folder and {total_lasx_files} lasx files in the [...\{lasx_directory}] folder")  # Printing the total counts of las and lasx files in their respective directories
        os._exit(0)  # Forcing the program to exit with a status code of 0

    signal.signal(signal.SIGINT, signal_handler)  # Registering the signal handler function for the SIGINT signal (Ctrl+C)
    
    try:  # Starting a try block to handle exceptions
        # Open the output CSV file and read its contents
        with open(output_file, 'r') as file:  # Opening the output CSV file in read mode using a context manager
            csv_reader = csv.reader(file)  # Creating a CSV reader object to read the contents of the output file
            
            # Skip the header row
            next(csv_reader)  # Skipping the header row of the output CSV file
            
            print("Cross-checking las and lasx files to see how many already exist...")  # Printing a message indicating the start of the cross-checking process
            
            # Perform cross-check for las and lasx files
            for row in csv_reader:  # Iterating over each row in the output CSV file
                lidar_url = row[0]  # Extracting the LiDAR URL from the current row
                file_name = os.path.basename(lidar_url)  # Extracting the file name from the LiDAR URL
                if os.path.exists(os.path.join(output_directory, file_name.replace('.zip', '.las'))):  # Checking if the corresponding las file already exists in the output directory
                    skipped_las_count += 1  # Incrementing the skipped las file counter
                else:  # If the las file doesn't exist
                    missing_las_count += 1  # Incrementing the missing las file counter
                if os.path.exists(os.path.join(lasx_directory, file_name.replace('.zip', '.lasx'))):  # Checking if the corresponding lasx file already exists in the lasx directory
                    skipped_lasx_count += 1  # Incrementing the skipped lasx file counter
                else:  # If the lasx file doesn't exist
                    missing_lasx_count += 1  # Incrementing the missing lasx file counter
            
            print(f"Cross-checking VanLidar2022_urls to lasx folder Completed.")  # Printing a message indicating the completion of the cross-checking process
            print(f"{skipped_las_count} las files and {skipped_lasx_count} lasx files already exist.")  # Printing the counts of skipped las and lasx files
            print(f"{missing_las_count} las files and {missing_lasx_count} lasx files are missing.")  # Printing the counts of missing las and lasx files
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
                if not os.path.exists(os.path.join(output_directory, file_name.replace('.zip', '.las'))) or not os.path.exists(os.path.join(lasx_directory, file_name.replace('.zip', '.lasx'))):  # Checking if either the las or lasx file doesn't exist
                    file_name, download_status, uncompress_status, las_count, lasx_count = download_and_extract(lidar_url)  # Calling the download_and_extract function to download and extract the ZIP file
                    if download_status == "downloaded":  # Checking if the ZIP file was successfully downloaded
                        downloaded_count += 1  # Incrementing the downloaded ZIP file counter
                    if uncompress_status == "uncompressed":  # Checking if the ZIP file was successfully uncompressed
                        uncompressed_las_count += las_count  # Incrementing the uncompressed las file counter by the count of extracted las files
                        uncompressed_lasx_count += lasx_count  # Incrementing the uncompressed lasx file counter by the count of extracted lasx files
                        removed_count += 1  # Incrementing the removed ZIP file counter
                
                # Update the progress bar with the counts after the ZIP file is removed
                progress_bar.set_postfix_str(f"{downloaded_count} ZIP files Downloaded, {uncompressed_las_count} las files and {uncompressed_lasx_count} lasx files Uncompressed, {removed_count} ZIP files Removed")  # Updating the progress bar with the current counts of downloaded, uncompressed, and removed files
                progress_bar.update(1)  # Updating the progress bar by 1 unit
        
        progress_bar.close()  # Closing the progress bar after all files have been processed
        
        print(f"Downloaded {downloaded_count} ZIP files, uncompressed {uncompressed_las_count} las files and {uncompressed_lasx_count} lasx files, and removed {removed_count} ZIP files.")  # Printing the final counts of downloaded, uncompressed, and removed files
        total_las_files = sum(1 for file in os.listdir(output_directory) if file.endswith('.las'))  # Counting the total number of las files in the output directory
        total_lasx_files = sum(1 for file in os.listdir(lasx_directory) if file.endswith('.lasx'))  # Counting the total number of lasx files in the lasx directory
        print(f"There are {total_las_files} las files in the [...\{output_directory}] folder and {total_lasx_files} lasx files in the [...\{lasx_directory}] folder")  # Printing the total counts of las and lasx files in their respective directories
    except Exception as e:  # Catching any exceptions that occur during the execution
        print(f"An error occurred: {str(e)}")  # Printing the error message
        print(f"Downloaded {downloaded_count} ZIP files, uncompressed {uncompressed_las_count} las files and {uncompressed_lasx_count} lasx files, and removed {removed_count} ZIP files before the error.")  # Printing the counts of downloaded, uncompressed, and removed files before the error occurred
        total_las_files = sum(1 for file in os.listdir(output_directory) if file.endswith('.las'))  # Counting the total number of las files in the output directory
        total_lasx_files = sum(1 for file in os.listdir(lasx_directory) if file.endswith('.lasx'))  # Counting the total number of lasx files in the lasx directory
        print(f"There are {total_las_files} las files in the [...\{output_directory}] folder and {total_lasx_files} lasx files in the [...\{lasx_directory}] folder")  # Printing the total counts of las and lasx files in their respective directories
else:
    print("Skipping the download and extraction process.")  # Printing a message indicating that the download and extraction process is being skipped
