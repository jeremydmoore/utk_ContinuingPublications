# importing & options
import datetime
import shutil
import tkinter as tk
from pathlib import Path
from tkinter.filedialog import askdirectory

def rename_files_to_directory_name(directory, zfill=4, file_extension='.tif'):

    '''
    creates a new 00_renamed directory at the same level as directory

    creates a directory inside of 00_renamed with the same name as directory

    copies all files with file_extension into 00_renamed/directory named: <directory>_<zfill><file_extension>

    returns Path of new directory if number of files copied is correct
    '''

    # set directory Path
    directory_path = Path(directory)

    # create 00_renamed directory at same level as directory and nested output_directory_path
    renamed_directory_path = directory_path.parents[0].joinpath('00_renamed')
    output_directory_path = renamed_directory_path.joinpath(directory_path.name)
    output_directory_path.mkdir(parents=True, exist_ok=True)

    # get filename stub for renaming
    filename_stub = directory_path.name
    file_paths_list = sorted(directory_path.glob(f'*{file_extension}'))
    number_of_files = len(file_paths_list)

    for index, file_path in enumerate(file_paths_list, start=1):
        new_filename = f'{filename_stub}_{str(index).zfill(zfill)}{file_extension}'
        new_file_path = output_directory_path.joinpath(new_filename)
        shutil.copyfile(file_path, new_file_path)

    renamed_file_paths_list = list(output_directory_path.glob(f'*{file_extension}'))
    if len(renamed_file_paths_list) == len(file_paths_list):
        print(f'Renamed {len(renamed_file_paths_list)} images in {directory_path}')
    else:
        print(f'***********ERROR**********:Renamed images: {len(renamed_file_paths_list)} does NOT match # to Rename: {len(file_paths_list)}')

    return output_directory_path

def create_subdirectories_for_ingest(book_directory, file_extension='.tif'):

    book_directory_path = Path(book_directory).resolve()
    print(f'Processing book at {book_directory_path}')

    # get sorted list of all image paths with file_extension
    image_paths_list = sorted([x for x in book_directory_path.iterdir() if str(x).endswith(file_extension)])
    number_of_images = len(image_paths_list)
    print(f'There are {number_of_images} "{file_extension}"s in "{book_directory_path}"')

    # set ingest stub to add to directory name
    ingest_stub = 'CreatedForIslandoraIngest'
    # get today's date in YYY-MM-DD format
    todays_date = datetime.datetime.now().strftime('%Y-%m-%d')
    # add today's date to ingest stub
    ingest_stub = f'{ingest_stub}_{todays_date}'

    # create ingest and output directory paths
    ingest_directory_path = book_directory_path.parents[1].joinpath('00_to_ingest')
    output_directory_name = f'{book_directory_path.name}_{ingest_stub}'
    output_directory_path = ingest_directory_path.joinpath(output_directory_name)
    output_directory_path.mkdir(parents=True, exist_ok=True)
    print(f'directory name for ingest: {output_directory_name}')

    print(f'To Process: {len(image_paths_list)} images in {book_directory_path}')

    # create a directory for an image then copy image into it
    for index, image_path in enumerate(image_paths_list, start=1):

        # create sub-directory for image
        image_directory_path = output_directory_path.joinpath(str(index))
        try:
            image_directory_path.mkdir()  # existing directory will throw error
        except FileExistsError:
            print(f'WARNING: ingest directory already exists at {image_directory_path} **********')

        # set copy image path & copy image
        copy_image_path = image_directory_path.joinpath(image_path.name)
        shutil.copyfile(image_path, copy_image_path)

        # set new image name to "page {index}{file_extension}"
        new_image_name = f'page {str(index)}{file_extension}'
        new_image_path = copy_image_path.parents[0].joinpath(new_image_name)

        # rename copied image path to new name
        copy_image_path.rename(new_image_path)

    glob_string = f'**/*{file_extension}'
    processed_image_paths_list = list(output_directory_path.glob(glob_string))
    number_of_processed_images = len(processed_image_paths_list)
    if len(processed_image_paths_list) == len(image_paths_list):
        print(f'Processed {len(processed_image_paths_list)} images in {ingest_directory_path}')
    else:
        print(f'***********ERROR**********: Processed images: {len(processed_image_paths_list)} does NOT match # to Process: {len(image_paths_list)}')

if __name__ == "__main__":

    # https://stackoverflow.com/a/14119223
    root = tk.Tk()
    root.withdraw()  # NO tk root window pop-up
    root_directory_path = Path(askdirectory())
    root.destroy()  # close tk window

    print(f'Root directory: {root_directory_path}')

    for directory_path in [x for x in root_directory_path.iterdir() if x.is_dir()]:
        print(f'Processing {directory_path}')

        # rename files to match <directory_name>_0001.tif
        renamed_files_directory_path = rename_files_to_directory_name(directory_path)

        create_subdirectories_for_ingest(renamed_files_directory_path)
