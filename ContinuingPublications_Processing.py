# ===== Imports
import tkinter as tk

from datetime import datetime
from dateutil.parser import parse
from pathlib import Path
from shutil import copytree, rmtree
from tkinter.filedialog import askdirectory


# ===== Functions
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

# ===== Classes

class ContinuingPublications_Volume:
    '''Common base class for Continuing Publications'''

    def __init__(self, directory, adminDB_collection, adminDB_item):
        self.directory_path = Path(directory).resolve()
        
        # set yaml path, rows, and rows list
        self.yaml_path = self.directory_path.parents[0].joinpath(f'{self.directory_path.name}.yml')  # yaml lives next to directory
        

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

        if backup_directory_path.exists():  # copytree requires directory to NOT exist
            # rmtree(backup_directory_path)
            print(f'Backup already exists at {backup_directory_path}')
        else:
            print(f'Backing up {self.directory_path.name} . . .')
            copytree(self.directory_path, backup_directory_path)

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

        # set ingest stub to add to directory name
        ingest_stub = 'ForIslandoraIngest'

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
            #copyfile(image_path, copy_image_path)
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
                elif pdf_path.stem.lower().endswith('edited'):
                    new_pdf_path = pdf_path.parents[0].joinpath('ORIGINAL_EDITED.pdf')
                else:  # don't rename
                    print(f'{pdf_path} is not original or original_edited, manually remediate')
                    print('')
                    continue
                # rename PDF
                print(f'Renaming {pdf_path.name} to {new_pdf_path}')
                print('')
                pdf_path.replace(new_pdf_path)      
                
class Playbills(ContinuingPublications_Volume):
    def __init__(self, directory, adminDB_collection, adminDB_item):
        # load ContinuingPublications_Volume class
        super().__init__(directory, adminDB_collection, adminDB_item)
        
        # get metadata from filename
        self.date, self.title = self.directory_path.name.split('_', maxsplit=1)
        self.title_replace_underscores = self.title.replace('_', ' ')
        self.yyyy, self.mm, self.dd = self.date.split('-')
        self.parsed_date = parse(self.date)
        self.month = self.parsed_date.strftime("%B")
        
        # cast self.dd as int to remove a possible leading zero
        self.date_issued = f'{self.month} {int(self.dd)}, {self.yyyy}'
        self.date_issued_edtf = self.date
        self.adminDB = f'0012_{str(adminDB_collection).zfill(6)}_{str(adminDB_item).zfill(6)}'
        self.yaml_row_0 = f'''adminDB: "{self.adminDB}"'''
        self.yaml_row_1 = f'''Title: "{self.title_replace_underscores}"'''
        self.yaml_row_2 = f'''date_Issued: "{self.date_issued}"'''
        self.yaml_row_3 = f'''date_Issued_edtf: "{self.date_issued_edtf}"'''
        self.yaml_rows_list = [self.yaml_row_0, self.yaml_row_1, self.yaml_row_2, self.yaml_row_3]
        
    def create_yaml(self):
        
        if self.yaml_path.is_file():
            print(f'{self.yaml_path} already exists')
            return
        else:  # create it
            print(f'Creating {self.yaml_path}')
            with open(self.yaml_path, 'a+') as yml_file:
                for yaml_row in self.yaml_rows_list:
                    yml_file.write(f'{yaml_row}\n')  # add line break
            # !touch "{self.yaml_path}"
            # for yaml_row in self.yaml_rows_list:
            #     print(f'Adding {yaml_row}')
            #     !echo "{yaml_row}" >> "{self.yaml_path}"
            # print(f'YAML data in {self.yaml_path}')
            !cat "{self.yaml_path}"
            return


if __name__ == "__main__":
    
    # !!!!!!
    # TODO: add batch or single directory processing
    
    # get file directory to process
    # https://stackoverflow.com/a/14119223
    root = tk.Tk()
    root.withdraw()  # NO tk root window pop-up
    directory_path = Path(askdirectory())
    root.destroy()  # close tk window

    print('')
    print(f'Directory: {directory_path}')
    print('')

    # !!!!!!
    # TODO: add choose continuing pub sub-class
    # load sub-class
    # rename
    # create YAML
    # create create ingest directory
    # move everything processed/created into a "book" directory
    # move everything else into a "backup" directory