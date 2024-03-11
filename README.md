# Data-Engineering-Project-Group-DE-I-11
Repo for the project in data engineering 1 

## Folder structure

**compute**: contains notebook for data analysis with either spark or only pandas. 
**data**: contains data created by data_handling and compute.
**data_handling**: contains notebooks for data handling: aggregating the million song dataset files into a single file, and making larger versions of it.
**images**: contains the images generated by compute files.

## Running the code
Make sure that there is a folder with the songs in h5 format, called MillionSongSubset for extracting the data (not included in the repo)
Run aggregate file (and enlarge if larger files are needed) before exectuting the computing. Make sure to be connected to a valid spark cluster if doing the spark computations
