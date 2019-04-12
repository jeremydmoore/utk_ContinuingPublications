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
            # shutil.rmtree(backup_directory_path)
            print(f'Backup already exists at {backup_directory_path}')
        else:
            print(f'Backing up {self.directory_path.name} . . .')
            shutil.copytree(self.directory_path, backup_directory_path)

            if backup_directory_path.exists():
                print('Backup created')
        return backup_directory_path.resolve()


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

        # set ingest stub to add to directory name
        ingest_stub = 'ForIslandoraIngest_Created'
        # get today's date in YYYY-MM-DD format and add to ingest stub
        todays_date = datetime.datetime.now().strftime('%Y-%m-%d')
        ingest_stub = f'{ingest_stub}_{todays_date}'

        # create ingest directory
        ingest_directory_name = f'{self.directory_path.name}_{ingest_stub}'
        ingest_directory_path = self.directory_path.parents[0].joinpath(ingest_directory_name)
        # try:
        #     ingest_directory_path.mkdir()
        # except FileExistsError:  # directory already exists
        #     print(f'WARNING: ingest directory already exists at {ingest_directory_path}')

        self.directory_path.replace(ingest_directory_path)

        image_paths_list = [x for x in ingest_directory_path.glob('*.tif')]
        number_of_images = len(image_paths_list)

        print(f'Processing {number_of_images} images in {self.directory_path.name}')

        # for each image
        for index, image_path in enumerate(image_paths_list, start=1):

            # create a sub-directory with a simple index number
            image_subdirectory_path = ingest_directory_path.joinpath(str(index).zfill(6))
            try:
                image_subdirectory_path.mkdir()
            except FileExistsError:
                print(f'Sub-directory already exists at {image_subdirectory_path}')

            # set new image name and copy path, then copy image
            #copy_image_path = image_subdirectory_path.joinpath(image_path.name)
            #shutil.copyfile(image_path, copy_image_path)
            image_path.replace(image_subdirectory_path.joinpath(image_path.name))

        print(f'Ingest directory created at {ingest_directory_path}')
        print('')

        return ingest_directory_path


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


    def rename_tiffs_to_directory_name(self, with_extension, zerofill=4):
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

        print(f'{number_of_files} with {formatted_extension}')

        if number_of_files == 0:
            pass

        else:  # rename files
            backup_directory_path = self.backup_volume()

            print(f'Renaming {number_of_files} "{formatted_extension}"s in {self.directory_path.name} . . .')

            count = 0
            try:
                for index, file_path in enumerate(file_paths_list, start=1):
                    # rename TIFF files from Adobe Acrobat for Islandora ingest, i.e. FILENAME.extension
                    new_file_name = f'{self.directory_path.name.upper()}_{str(index).zfill(zerofill)}{remediated_extension}'
                    new_file_path = file_path.parents[0].joinpath(new_file_name)
                    file_path.replace(new_file_path)
                    count = index
            except IndexError:
                pass

            print(f' Renamed {count} "{formatted_extension}"s')
            print('')


    def rename_PDFs_for_ingest(self):

        pdf_paths_list = self.get_file_paths('.pdf')

        number_of_pdfs = len(pdf_paths_list)
        if number_of_pdfs == 0:
            print(f'{number_of_pdfs} PDFs to process')
        else:  # process PDFs
            for pdf_path in pdf_paths_list:
                # expect PDF stems ending in original or processed
                if pdf_path.stem.lower().endswith('original'):
                    new_pdf_path = pdf_path.parents[0].joinpath('ORIGINAL.pdf')
                elif pdf_path.stem.lower().endswith('processed'):
                    new_pdf_path = pdf_path.parents[0].joinpath('PROCESSED.pdf')
                else:  # don't rename
                    print(f'{pdf_path} is not original or processed, manually remediate')
                    print('')
                    continue
                # rename PDF
                print(f'Renaming {pdf_path.name} to {new_pdf_path}')
                print('')
                pdf_path.replace(new_pdf_path)

if __name__ == "__main__":

    # get file directory to process
    # https://stackoverflow.com/a/14119223
    root = tk.Tk()
    root.withdraw()  # NO tk root window pop-up
    root_directory_path = Path(askdirectory())
    root.destroy()  # close tk window

    directory_paths_list = [x for x in root_directory_path.iterdir() if x.is_dir()]

    for directory_path in directory_paths_list:
        print('')
        print(f'Directory: {directory_path}')
        print('')

        # create Volume
        volume = ContinuingPublications_Volume(directory_path)

        # rename Adobe Acrobat .tiff files to directory and .tif extension
        volume.rename_tiffs_to_directory_name('.tiff')
        volume.rename_tiffs_to_directory_name('.tif')

        # rename PDFs for ingest
        volume.rename_PDFs_for_ingest()

        # create Islanodra book ingest directory
        ingest_directory_path = volume.create_islandora_ingest_directory()

        # create book directory path as needed for Islandora
        book_directory_path = volume.directory_path.parents[0].joinpath('book')
        book_directory_path.mkdir(exist_ok=True)

        # move ingest directory into book directory
        final_path = book_directory_path.joinpath(ingest_directory_path.name)
        ingest_directory_path.replace(final_path)

        number_of_books = len([x for x in book_directory_path.iterdir() if x.is_dir()])
        print(f'{number_of_books} books in {book_directory_path} for ingest')
        print('')

    # keep command window open after running PyInstaller
    print('Press Enter key to close window')
    input()
