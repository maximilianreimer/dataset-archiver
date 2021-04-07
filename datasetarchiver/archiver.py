import hashlib
import tarfile
import tempfile

import json
from datetime import datetime
from os import PathLike

from pathlib import Path
from typing import List, Tuple
from zipfile import ZipFile

META_DATA_FILE = 'meta.json'


def load_meta_file(dataset_path: Path):
    """

    Loads the meta data file
    :param dataset_path:
    :return:
    """
    meta_file_path = dataset_path / META_DATA_FILE
    if not meta_file_path.exists():
        raise FileNotFoundError(f'File ({meta_file_path} does not exits!')

    with open(meta_file_path, 'r') as meta_file:
        meta = json.load(meta_file)
    return meta


def reset_tar_info(tar_info: tarfile.TarInfo):
    """
    Removes file system specific infos to be able to create unambiguous chechsums

    :param tar_info:
    :return:
    """

    RESET_FIELDS = {
        'mtime': 0,
        'mode': 420,
        'uid': 0,
        'gid': 0,
        'uname': '',
        'gname': '',
    }

    for key, default_value in RESET_FIELDS.items():
        tar_info.__setattr__(key, default_value)

    return tar_info


def md5(file: PathLike) -> str:
    """
    Calulates the md5 checksum of a given file
    :param file:
    :return:
    """
    hash_md5 = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def archive_raw_dataset(source_path: Path, archive_path: Path):
    f"""
    Create a tar containing all files in source path except {META_DATA_FILE} and removes the file system specific info
    :param source_path: 
    :param archive_path: 
    :return: 
    """
    all_but_meta = lambda tar_info: reset_tar_info(tar_info) if tar_info.name != META_DATA_FILE else None
    with tarfile.open(archive_path, 'x', format=tarfile.GNU_FORMAT) as tar_file:
        tar_file.add(source_path, filter=all_but_meta)


def _archive_raw_dataset(source_path: Path, archive_path: Path):
    f"""
    Create a tar containing all files in source path except {META_DATA_FILE} and removes the file system specific info
    :param source_path: 
    :param archive_path: 
    :return: 
    """
    all_but_meta = filter(lambda file: file.name != META_DATA_FILE ,source_path.rglob('*'))
    with ZipFile(archive_path, 'w') as archive_file:
        for f in all_but_meta:
            archive_file.write(f, all_but_meta)

def tar_archive_dataset(archive_path :Path, archive_name : str, files : List[Tuple[PathLike, str]]):
    result_archive_file = archive_path / f'{archive_name}.tar'
    with tarfile.open(result_archive_file, 'x:gz') as tar_file:
        for file, name in files:
            tar_file.add(file, arcname=name)
    return result_archive_file

def zip_archive_dataset(archive_path :Path, archive_name : str, files : List[Tuple[PathLike, str]]):
    result_archive_file = archive_path / f'{archive_name}.tar'
    with tarfile.open(result_archive_file, 'x:gz') as tar_file:
        for file, name in files:
            tar_file.add(file, arcname=name)
    return result_archive_file

def archive_dataset(source_path: Path, archive_path: Path, meta_json: dict = None) -> Path:
    """

    :param source_path:
    :param archive_path:
    :param meta_json:
    :return:
    """
    meta_json = meta_json if meta_json is not None else {}
    # if dataset path does not exits create it
    archive_path.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tempdir:
        tempdir = Path(tempdir)

        # create data gz.tar (everything) within the source path (meta.json) in temp dir
        source_dir_name = source_path.name
        data_tar_name = f'{source_dir_name}.tar.gz'
        temp_tar = tempdir / data_tar_name
        archive_raw_dataset(source_path, temp_tar)

        # create the meta.json and update with meta_json and exiting data
        new_meta = {
            'name': source_dir_name
        }
        try:
            source_meta = load_meta_file(source_path)
        except FileNotFoundError as e:
            source_meta = {}
        source_meta['source']: source_meta.get('name', '') + source_meta.get('md5checksum', '')
        new_meta.update(source_meta)
        new_meta.update(meta_json)
        new_meta.update({
            'creation_date': datetime.now().isoformat(),
            'md5checksum': md5(temp_tar)
        })
        meta_file = tempdir / META_DATA_FILE
        with open(meta_file, 'w') as f:
            json.dump(new_meta, f)

        # create resulting tar in dataset_path
        archive_name = '_'.join([new_meta['name'], new_meta['creation_date']])

        return result_archive_file
