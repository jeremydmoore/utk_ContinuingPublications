import shutil
import tkinter as tk
from pathlib import Path
from tkinter.filedialog import askdirectory

def get_formatted_extension(from_extension, remediate=False):
    '''
    -- Purpose --
    Returns an extension that:
    1. has a period in the front
    2. Optional: is lower-case
    3. Optional: return jpeg as jpg and tiff as tif

    -- Arguments --
    from_extension: type=string; file extension with or without a '.'

    -- Returns --
    formatted_extension: type=string; formatted extension
    '''
    # make sure there's a period at the front of the extension
    if from_extension.startswith('.'):  # do nothing
        formatted_extension = from_extension
    else:  # add a period
        formatted_extension = f'.{from_extension}'

    # make it lower-case
    if remediate:
        formatted_extension = formatted_extension.lower()
        # hard-coded alterations for jpeg and tiff
        if formatted_extension == '.jpeg':
            formatted_extension = '.jpg'
        elif formatted_extension == '.tiff':
            formatted_extension = '.tif'

    return formatted_extension

class ContinuingPublications_Volume:
    '''Common base class for Continuing Publications'''

    def __init__(self, directory):
        self.directory_path = Path(directory).resolve()

    def backup_volume(self):
        '''
        -- Purpose --
        Copy all files in directory to backup directory with name: <directory>_backup

        -- Arguments --
        None

        -- Returns --
        backup_directory_path: type=Path-like object; returns absolute path to backup directory
        '''
        backup_directory_name = f'{self.directory_path.name}_backup'
        backup_directory_path = self.directory_path.parents[0].joinpath(backup_directory_name)

        if backup_directory_path.exists():  # shutil.copytree requires directory to NOT exist
            shutil.rmtree(backup_directory_path)

        shutil.copytree(self.directory_path, backup_directory_path)

        if backup_directory_path.exists():
            return backup_directory_path.resolve()

    def remove_backup(self):
        '''
        -- Purpose --
        Deletes the backup volume created by self.backup_volume()

        -- Arguments --
        None

        -- Returns --
        True/False: type=boolean; True/False result of _backup.is_dir()
        '''
        backup_directory_name = f'{self.directory_path.name}_backup'
        backup_directory_path = self.directory_path.parents[0].joinpath(backup_directory_name)

        # remove backup directory
        shutil.rmtree(backup_directory_path)

        return backup_directory_path.is_dir()

    def undo_backup(self):
        '''
        -- Purpose --
        Deletes the processed directory and renames the backup directory to the
        original directory name

        -- Arguments --
        None

        -- Returns --
        None
        '''
        backup_directory_name = f'{self.directory_path.name}_backup'
        backup_directory_path = self.directory_path.parents[0].joinpath(backup_directory_name)

        # remove processed directory
        shutil.rmtree(self.directory_path)

        # rename backup directory to original directory name
        backup_directory_path.rename(self.directory_path)

    def get_file_paths(self, with_extension):
        '''
        -- Purpose --
        Get all file Paths with_extension in self.directory_path

        -- Arguments --
        with_extension: type=string; extension to use for globbing

        -- Returns --
        file_paths_list: type:list; list of Path-like objects, 1 Path-like object
        per file_path in self.directory_path
        '''
        formatted_extension = get_formatted_extension(with_extension)
        file_paths_list = sorted(self.directory_path.glob(f'*{formatted_extension}'))
        return file_paths_list

    def rename_files_to_directory_name(self, with_extension, zerofill=4):
        '''
        -- Purpose --
        Rename all files {with_extension} to {self.directory_path.name}_{str(index).zfill(zerofill)}
        *Note: will currently remediate extensions to lower-case and change tiff/jpeg to tif/jpg

        -- Arguments --
        with_extension: type=string; extension to rename
        zerofill: type=integer; how many digits to zeropad

        -- Returns --
        None
        '''
        formatted_extension = get_formatted_extension(with_extension)

        # extension will be lower-case and tif/jpg instead of tiff/jpeg
        remediated_extension = get_formatted_extension(with_extension, remediate=True)

        # get total number of files and the paths for files to rename
        file_paths_list = self.get_file_paths(formatted_extension)
        number_of_files = len(file_paths_list)

        backup_directory_path = self.backup_volume()

        if backup_directory_path.exists():
            print(f'Backup directory created at {backup_directory_path}')

        print(f'Renaming {number_of_files} "{formatted_extension}"s in {self.directory_path.name} . . .')

        count = 0
        for index, file_path in enumerate(file_paths_list, start=1):
            new_file_name = f'{self.directory_path.name}_{str(index).zfill(zerofill)}{remediated_extension}'
            new_file_path = file_path.parents[0].joinpath(new_file_name)
            file_path.rename(new_file_path)
            count = index

        print(f' Renamed {count} "{formatted_extension}"s')

    def create_islandora_ingest_directory(self):
        '''
        -- Purpose --
        Create Islandora ingest directory with TIFF in nested structure

        -- Arguments --
        None

        -- Returns --
        ingest_directory_path: type=Path-like object; Path to the directory for ingest
        '''
        import datetime

        # get image paths and number of images
        extension = 'tif'
        image_paths_list = self.get_file_paths(extension)
        number_of_images = len(image_paths_list)

        # set ingest stub to add to directory name
        ingest_stub = 'CreatedForIslandoraIngest'
        # get today's date in YYYY-MM-DD format and add to ingest stub
        todays_date = datetime.datetime.now().strftime('%Y-%m-%d')
        ingest_stub = f'{ingest_stub}_{todays_date}'

        # create ingest directory
        ingest_directory_name = f'{self.directory_path.name}_{ingest_stub}'
        ingest_directory_path = self.directory_path.parents[0].joinpath(ingest_directory_name)
        try:
            ingest_directory_path.mkdir()
        except FileExistsError:  # directory already exists
            print(f'WARNING: ingest directory already exists at {ingest_directory_path}')

        print(f'Processing {number_of_images} in {self.directory_path.name}')

        # for each image
        for index, image_path in enumerate(image_paths_list, start=1):

            # create a sub-directory with a simple index number
            image_subdirectory_path = ingest_directory_path.joinpath(str(index))
            try:
                image_subdirectory_path.mkdir()
            except FileExistsError:
                print(f'Sub-directory already exists at {image_subdirectory_path}')

            # set new image name and copy path, then copy image
            new_image_name = f'page {str(index)}{image_path.suffix}'
            copy_image_path = image_subdirectory_path.joinpath(new_image_name)
            shutil.copyfile(image_path, copy_image_path)

        return ingest_directory_path

    def create_zip_file(self, directory_to_zip):
        '''
        -- Purpose --
        Create a zip file from directory_path
        To be used with create_islandora_ingest_directory

        -- Arguments --
        directory_path: type=Path-like object; directory to compress into a Zip file

        -- Returns --
        True/False: type=boolean; whether or not {directory_path.name}.zip exists
        in {directory_path.parents[0]}
        '''
        directory_to_zip_path = Path(directory_to_zip)
        shutil.make_archive(self.directory_path, "zip", root_dir=directory_to_zip_path)

if __name__ == "__main__":

    # get file directory to process
    # https://stackoverflow.com/a/14119223
    root = tk.Tk()
    root.withdraw()  # NO tk root window pop-up
    directory_path = Path(askdirectory())
    root.destroy()  # close tk window

    print('')
    print(f'Directory: {directory_path}')
    print('')

    # create Volume
    volume = ContinuingPublications_Volume(directory_path)

    # rename files
    volume.rename_files_to_directory_name('.tiff')

    # create Islanodra ingest file
    ingest_directory_path = volume.create_islandora_ingest_directory()

    # create zip file
    volume.create_zip_file(ingest_directory_path)
