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
        Remove the backup volume created by self.backup_volume()

        -- Arguments --
        None

        -- Returns --
        True/False: type=boolean; True/False result of _backup.is_dir()
        '''
        backup_directory_name = f'{self.directory_path.name}_backup'
        backup_directory_path = self.directory_path.parents[0].joinpath(backup_directory_path)

        # remove backup directory
        shutil.rmtree(backup_directory_path)

        return backup_directory_path.is_dir()

    def undo_backup(self):
        backup_directory_name = f'{self.directory_path.name}_backup'
        backup_directory_path = self.directory_path.parents[0].joinpath(backup_directory_name)

        # remove processed directory
        shutil.rmtree(self.directory_path)

        # rename backup directory to original directory name
        backup_directory_path.rename(self.directory_path)

    def get_file_paths(self, with_extension):
        formatted_extension = get_formatted_extension(with_extension)
        file_paths_list = sorted(self.directory_path.glob(f'*{formatted_extension}'))
        return file_paths_list

    def rename_files_to_directory_name(self, with_extension, zerofill=4):

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

    def create_islandora_ingest(self):
        '''
        -- Purpose --
        Create Islandora ingest directory

        -- Arguments --
        None

        -- Returns --

        '''

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
