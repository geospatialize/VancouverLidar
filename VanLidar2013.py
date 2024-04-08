import csv  # Import the csv module for reading and writing CSV files
import os  # Import the os module for file and directory operations
import requests  # Import the requests module for making HTTP requests
import zipfile  # Import the zipfile module for extracting ZIP files
from tqdm import tqdm  # Import the tqdm module for progress bars
import signal  # Import the signal module for handling signals like SIGINT (Ctrl+C)

# Input CSV file path
input_file = 'lidar-2013.csv'  # Specify the path to the input CSV file

# Output CSV file path to store the extracted URLs
output_file_lidar = 'VanLidar2013_urls.csv'  # Specify the path to the output CSV file for LiDAR URLs
output_file_geotiff = 'VanGeoTiff2013_urls.csv'  # Specify the path to the output CSV file for GeoTIFF URLs

# Directory to store the downloaded and uncompressed files
output_directory_lidar = 'VanLidar2013'  # Specify the directory to store the downloaded and uncompressed LiDAR files
output_directory_geotiff = 'VanGeoTiff2013'  # Specify the directory to store the downloaded and uncompressed GeoTIFF files

# Create the output directories if they don't exist
os.makedirs(output_directory_lidar, exist_ok=True)  # Create the output directory for LiDAR files if it doesn't exist
os.makedirs(output_directory_geotiff, exist_ok=True)  # Create the output directory for GeoTIFF files if it doesn't exist

# Open the input CSV file and read its contents
with open(input_file, 'r') as file:  # Open the input CSV file in read mode
    csv_reader = csv.reader(file)  # Create a CSV reader object to read the contents of the file
    
    # Skip the header row
    next(csv_reader)  # Skip the header row of the CSV file
    
    # Open the output CSV files to write the extracted URLs
    with open(output_file_lidar, 'w', newline='') as output_lidar, open(output_file_geotiff, 'w', newline='') as output_geotiff:
        # Open the output CSV files for LiDAR and GeoTIFF URLs in write mode
        csv_writer_lidar = csv.writer(output_lidar)  # Create a CSV writer object for the LiDAR URLs file
        csv_writer_geotiff = csv.writer(output_geotiff)  # Create a CSV writer object for the GeoTIFF URLs file
        
        # Write the header row in the output CSV files
        csv_writer_lidar.writerow(['LiDAR_URL'])  # Write the header row for the LiDAR URLs file
        csv_writer_geotiff.writerow(['GeoTIFF_URL'])  # Write the header row for the GeoTIFF URLs file
        
        # Initialize counters for the number of extracted URLs
        lidar_url_count = 0  # Initialize a counter for the number of extracted LiDAR URLs
        geotiff_url_count = 0  # Initialize a counter for the number of extracted GeoTIFF URLs
        
        # Iterate over each row in the input CSV file
        for row in csv_reader:  # Iterate over each row in the input CSV file
            # Split the first column by semicolon to get the values
            values = row[0].split(';')  # Split the first column of the row by semicolon to get individual values
            
            # Extract the LiDAR URL from the third value
            lidar_url = values[2]  # Extract the LiDAR URL from the third value in the split row
            
            # Extract the GeoTIFF URL from the second value
            geotiff_url = values[1]  # Extract the GeoTIFF URL from the second value in the split row
            
            # Write the URLs as rows in the respective output CSV files
            csv_writer_lidar.writerow([lidar_url])  # Write the LiDAR URL as a row in the LiDAR URLs file
            csv_writer_geotiff.writerow([geotiff_url])  # Write the GeoTIFF URL as a row in the GeoTIFF URLs file
            
            # Increment the URL counters
            lidar_url_count += 1  # Increment the counter for extracted LiDAR URLs
            geotiff_url_count += 1  # Increment the counter for extracted GeoTIFF URLs

print(f"{lidar_url_count} LiDAR URLs extracted and saved to {output_file_lidar}")  # Print the number of extracted LiDAR URLs and the output file path
print(f"{geotiff_url_count} GeoTIFF URLs extracted and saved to {output_file_geotiff}")  # Print the number of extracted GeoTIFF URLs and the output file path

# Function to download and extract files
def download_and_extract_files(output_file, output_directory, file_extensions):
    # Count the number of URLs in the output CSV file
    with open(output_file, 'r') as file:  # Open the output CSV file in read mode
        csv_reader = csv.reader(file)  # Create a CSV reader object to read the contents of the file
        num_files = sum(1 for _ in csv_reader) - 1  # Count the number of URLs in the file (excluding the header row)

    # Prompt the user for a response
    user_response = input(f"Do you want to proceed with downloading and extracting {num_files} files? (Y/y/N/n): ")  # Prompt the user for confirmation

    if user_response.lower() in ['y', 'yes']:  # If the user confirms to proceed
        downloaded_count = 0  # Initialize a counter for the number of downloaded ZIP files
        uncompressed_count = 0  # Initialize a counter for the number of uncompressed files
        removed_count = 0  # Initialize a counter for the number of removed ZIP files
        skipped_count = {ext: 0 for ext in file_extensions}  # Initialize a dictionary to store the count of skipped files for each file extension
        missing_count = {ext: 0 for ext in file_extensions}  # Initialize a dictionary to store the count of missing files for each file extension

        def download_and_extract(url):
            file_name = os.path.basename(url)  # Extract the file name from the URL
            zip_file_path = os.path.join(output_directory, file_name)  # Create the full path to the ZIP file
            
            response = requests.get(url, stream=True)  # Send a GET request to download the file
            total_size = int(response.headers.get('content-length', 0))  # Get the total size of the file from the response headers
            block_size = 1024  # Set the block size for downloading the file
            
            with open(zip_file_path, 'wb') as zip_file:  # Open the ZIP file in write binary mode
                for data in response.iter_content(block_size):  # Iterate over the file content in blocks
                    zip_file.write(data)  # Write each block of data to the ZIP file
            
            file_counts = {ext: 0 for ext in file_extensions}  # Initialize a dictionary to store the count of extracted files for each file extension
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:  # Open the ZIP file for reading
                for file in zip_ref.namelist():  # Iterate over the files in the ZIP archive
                    for ext in file_extensions:  # Iterate over the specified file extensions
                        if file.endswith(ext):  # If the file has the specified extension
                            zip_ref.extract(file, output_directory)  # Extract the file to the output directory
                            file_counts[ext] += 1  # Increment the count of extracted files for the corresponding file extension
            
            os.remove(zip_file_path)  # Remove the ZIP file after extraction
            
            return file_name, "downloaded", "uncompressed", file_counts  # Return the file name, download status, uncompress status, and file counts

        def signal_handler(sig, frame):
            print("\nProcess terminated by user.")  # Print a message indicating that the process was terminated by the user
            print(f"Downloaded {downloaded_count} ZIP files, uncompressed {uncompressed_count} files, and removed {removed_count} ZIP files before termination.")  # Print the counts before termination
            for ext in file_extensions:  # Iterate over the specified file extensions
                total_files = sum(1 for file in os.listdir(output_directory) if file.endswith(ext))  # Count the total number of files with the specified extension in the output directory
                print(f"There are {total_files} {ext} files in the [...\{output_directory}] folder")  # Print the count of files for each file extension
            os._exit(0)  # Exit the program with status code 0

        signal.signal(signal.SIGINT, signal_handler)  # Register the signal handler for SIGINT (Ctrl+C)
        
        try:
            # Open the output CSV file and read its contents
            with open(output_file, 'r') as file:  # Open the output CSV file in read mode
                csv_reader = csv.reader(file)  # Create a CSV reader object to read the contents of the file
                
                # Skip the header row
                next(csv_reader)  # Skip the header row of the CSV file
                
                print(f"Cross-checking {', '.join(file_extensions)} files to see how many already exist...")  # Print a message indicating the cross-checking process
                
                # Perform cross-check for files
                for row in csv_reader:  # Iterate over each row in the CSV file
                    url = row[0]  # Get the URL from the first column of the row
                    file_name = os.path.basename(url)  # Extract the file name from the URL
                    for ext in file_extensions:  # Iterate over the specified file extensions
                        if os.path.exists(os.path.join(output_directory, file_name.replace('.zip', ext))):  # If the file with the specified extension already exists in the output directory
                            skipped_count[ext] += 1  # Increment the count of skipped files for the corresponding file extension
                        else:
                            missing_count[ext] += 1  # Increment the count of missing files for the corresponding file extension
                
                print(f"Cross-checking {output_file} to {output_directory} folder Completed.")  # Print a message indicating the completion of the cross-checking process
                for ext in file_extensions:  # Iterate over the specified file extensions
                    print(f"{skipped_count[ext]} {ext} files already exist.")  # Print the count of skipped files for each file extension
                    print(f"{missing_count[ext]} {ext} files are missing.")  # Print the count of missing files for each file extension
                print(f"Initializing Downloading Process...")  # Print a message indicating the initialization of the downloading process
                
                # Create a progress bar for the overall process
                progress_bar = tqdm(total=num_files, unit='file', desc='Overall Progress', leave=False)  # Create a progress bar for the overall process
                
                # Reset the file pointer to the beginning of the CSV file
                file.seek(0)  # Reset the file pointer to the beginning of the CSV file
                next(csv_reader)  # Skip the header row again
                
                # Iterate over each row in the CSV file
                for row in csv_reader:  # Iterate over each row in the CSV file
                    url = row[0]  # Get the URL from the first column of the row
                    file_name = os.path.basename(url)  # Extract the file name from the URL
                    if any(not os.path.exists(os.path.join(output_directory, file_name.replace('.zip', ext))) for ext in file_extensions):  # If any of the specified file extensions are missing for the file
                        file_name, download_status, uncompress_status, file_counts = download_and_extract(url)  # Download and extract the file
                        if download_status == "downloaded":
                            downloaded_count += 1  # Increment the count of downloaded ZIP files
                        if uncompress_status == "uncompressed":
                            uncompressed_count += 1  # Increment the count of uncompressed files
                            removed_count += 1  # Increment the count of removed ZIP files
                    
                    # Update the progress bar with the counts after the ZIP file is removed
                    progress_bar.set_postfix_str(f"{downloaded_count} ZIP files Downloaded, {uncompressed_count} files Uncompressed, {removed_count} ZIP files Removed")  # Update the progress bar with the counts
                    progress_bar.update(1)  # Update the progress bar by one unit
            
            progress_bar.close()  # Close the progress bar
            
            print(f"Downloaded {downloaded_count} ZIP files, uncompressed {uncompressed_count} files, and removed {removed_count} ZIP files.")  # Print the final counts
            for ext in file_extensions:  # Iterate over the specified file extensions
                total_files = sum(1 for file in os.listdir(output_directory) if file.endswith(ext))  # Count the total number of files with the specified extension in the output directory
                print(f"There are {total_files} {ext} files in the [...\{output_directory}] folder")  # Print the count of files for each file extension
        except Exception as e:
            print(f"An error occurred: {str(e)}")  # Print an error message if an exception occurs
            print(f"Downloaded {downloaded_count} ZIP files, uncompressed {uncompressed_count} files, and removed {removed_count} ZIP files before the error.")  # Print the counts before the error
            for ext in file_extensions:  # Iterate over the specified file extensions
                total_files = sum(1 for file in os.listdir(output_directory) if file.endswith(ext))  # Count the total number of files with the specified extension in the output directory
                print(f"There are {total_files} {ext} files in the [...\{output_directory}] folder")  # Print the count of files for each file extension
    else:
        print("Skipping the download and extraction process.")  # Print a message indicating that the download and extraction process is skipped

# Download and extract LiDAR files
print("Processing LiDAR files...")  # Print a message indicating the processing of LiDAR files
download_and_extract_files(output_file_lidar, output_directory_lidar, ['.las'])  # Call the function to download and extract LiDAR files

# Download and extract GeoTIFF files
print("Processing GeoTIFF files...")  # Print a message indicating the processing of GeoTIFF files
download_and_extract_files(output_file_geotiff, output_directory_geotiff, ['.tif', '.tfw'])  # Call the function to download and extract GeoTIFF files
