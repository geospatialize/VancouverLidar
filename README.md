# Vancouver LiDAR Data Downloader

## Disclaimer
This repository contains Python code to bulk download publicly available LiDAR data from [City of Vancouver Open Data Portal](https://opendata.vancouver.ca/pages/home/) for a specified year. 
Please note the following:
1. I am not affiliated with the City of Vancouver in any way. This code is developed and shared by me as a GIS enthusiast and is not an official resource provided by the City of Vancouver.
2. The code is provided "as is" without warranty of any kind, express or implied. Use at your own discretion.
3. It is the user's responsibility to comply with the City of Vancouver's terms of service, licensing agreements, and any other applicable policies when accessing and using the downloaded data. Make sure you have the necessary permissions and licenses before using the data for any purpose.
4. I am not liable for any damages, losses, or issues that may arise from using the code or the downloaded data. This includes, but is not limited to, data inaccuracies, data misuse, software errors, or violation of terms of service.
5. Downloading large datasets may consume significant bandwidth and storage space. Ensure that you have sufficient resources and network capacity before running the code. Be mindful of any usage restrictions or rate limits imposed by the City of Vancouver.
6. The code is intended for educational and research purposes only. If you plan to use the downloaded data for commercial or production purposes, please consult the City of Vancouver's licensing terms and obtain the necessary permissions.
7. If you encounter any issues or have questions regarding the data, please contact the City of Vancouver directly. I am not responsible for providing support or addressing data-related inquiries.

By using this code and downloading the LiDAR data, you acknowledge that you have read, understood, and agreed to the terms and conditions outlined in this disclaimer.

## Python Code to download the City of Vancouver's Lidar Data (Vancouver, British Columbia)
This repository contains Python scripts to download LiDAR data for the City of Vancouver from 2013, 2018, and 2022 and download GeoTIFF data from 2013.


### Prerequisites
To run the Python scripts in this repository, you need to have the following installed:
- Python 3.x
- Required Python packages: `csv`, `os`, `requests`, `zipfile`, `tqdm`, `signal`
- I have tried to use as much PSL (Python Standard Library) as much as possible but you may have to install `requests` and `tqdm`.

You can install these packages using pip:
```
pip install requests tqdm
```

## User Guide
1. Clone this repository to your local machine or download the CSV and Python (.py) files of the same year to a path where you want to store all the LiDAR data (e.g., `lidar-2022.csv` and `lidar_downloader_2022.py`). 
2. Open your preferred Python IDE (e.g., VS Code).
3. Run the Python script for the desired year (e.g., `lidar_downloader_2022.py`).
   - The script will automatically save all the download URLs for the LiDAR data (and GeoTIFF for 2013) into another CSV file (e.g., `VanLidar2022_urls.csv`) and print a completion statement.
4. The script will prompt the user: "Do you want to proceed with downloading and extracting X files? (Y/y/N/n)". 
   - If the user enters 'Y' or 'y', the script will proceed to download the data.
   - If the user enters 'N' or 'n', the script will skip the download process.
5. The script will start downloading the ZIP files, extracting the contents, and removing the ZIP files. The progress will be displayed in the console. You can interrupt the downloading process at any time by pressing Ctrl+C.
   You will know when you have interrupted when the statement "Process terminated by user." appears on the terminal.
   - Once the download and extraction process is complete, you will find the downloaded files in the following directories:

     For 2013 data:
     - LiDAR files: `VanLidar2013`
     - GeoTIFF files: `VanGeoTiff2013`

     For 2018 data:
     - LiDAR files: `VanLidar2018`
     - Projection files: `VanLidar2018/prj`

     For 2022 data:
     - LAS files: `VanLidar2022`
     - LASX files: `VanLidar2022/lasx`

Notes:
- The scripts will create the necessary output directories if they don't exist.
- If the download process is interrupted, you can re-run the script, and it will skip the files that have already been downloaded and extracted.
- The scripts provide progress updates and display the counts of downloaded, extracted, and removed files.

## Data Sources
- Vancouver Lidar 2022: [https://opendata.vancouver.ca/explore/dataset/lidar-2022/](https://opendata.vancouver.ca/explore/dataset/lidar-2022/)
- Vancouver Lidar 2018: [https://opendata.vancouver.ca/explore/dataset/lidar-2018/](https://opendata.vancouver.ca/explore/dataset/lidar-2018/)
- Vancouver Lidar 2013: [https://opendata.vancouver.ca/explore/dataset/lidar-2013/](https://opendata.vancouver.ca/explore/dataset/lidar-2013/)

## Contributing
Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.
