import argparse

import sys
import hashlib

from pathlib import Path, PurePosixPath
from typing import Dict, Tuple

from datasetarchiver.archiver import load_meta_file, md5


def is_valid_file(arg):
    path = Path(arg)
    if not path.exists() or not path.is_dir():
        raise argparse.ArgumentTypeError("The folder %s does not exist!" % arg)
    else:
        return path


exclude_files = ["meta.json"]


def get_checksums(dataset_path: Path) -> Dict[str, Dict["str", "str"]]:
    """
    Calculated for all files in the dataset_path (except the meta.json) the md5 hash
    and returns a dict of the form
    {
       'relative/path/to/file': checksum, ...
    }
    :param dataset_path:
    :return:
    """
    files = filter(lambda file: file.name not in exclude_files, dataset_path.rglob("*"))
    files = filter(lambda file: not file.is_dir(), files)
    return {
        str(PurePosixPath(file.relative_to(dataset_path))): md5(file) for file in files
    }


def overall_checksum(checksums: Dict[str, str]):
    hash = hashlib.md5()
    for file, checksum in sorted(checksums.items(), key=lambda ky: ky[0]):
        hash.update((file + checksum).encode("utf-8"))
    return hash.hexdigest()


def check_checksums(
    checksums_a: Dict[str, str], checksums_b: Dict[str, str]
) -> Dict[str, Tuple[str, str]]:
    """
    Comapres to sets of checksum and returns a dict
    {
        'relative/path/to/file: (checksum_a, checkusm_b) , ...
    }

    for all checksums that differ. If a file does only exits in one dict,
    checksum is None.
    :param checksums_a:
    :param checksums_b:
    :return:
    """

    keys = set(checksums_b.keys()) | set(checksums_a.keys())
    return {
        key: (checksums_a.get(key, None), checksums_b.get(key, None))
        for key in keys
        if checksums_a.get(key, None) != checksums_b.get(key, None)
        or (key not in checksums_a and key not in checksums_b)
    }


def check(dataset_dir_a: Path, dataset_dir_b: Path):
    meta_a = load_meta_file(dataset_dir_a)
    meta_b = load_meta_file(dataset_dir_b)

    if meta_a["md5checksum"] != meta_b["md5checksum"]:
        print("Datasets are different")
    else:
        print("Datasets are the same.")


def main(args):
    parser = argparse.ArgumentParser(
        "Utility to crate dataset archive and store additional meta data."
        "The resulting dataset archive will contain a meta.json containing a"
        "unique md5 checksum of the dataset as well as other useful inforamtion"
    )
    sub_parsers = parser.add_subparsers(dest="command")

    update_parser = sub_parsers.add_parser(
        "create", help="Creates a archive containing the dataset and the meta data"
    )

    update_parser.add_argument(
        "--dataset_dir",
        type=is_valid_file,
        required=True,
        help="Directory of the dataset",
    )
    update_parser.add_argument(
        "--meta_data",
        type=str,
        default=None,
        required=False,
        help="A string following the json format, used to updated the values of"
        " the meta.json.",
    )

    check_parser = sub_parsers.add_parser(
        "check", help="Checks if two dataset are the same (according to the meta data)"
    )
    check_parser.add_argument("--dataset_dir_a", type=is_valid_file, required=True)
    check_parser.add_argument("--dataset_dir_b", type=is_valid_file, required=True)

    args = parser.parse_args(args)

    if args.command == "update":
        ...
        # update_dataset_meta(args.dataset_dir, json.loads(args.meta_data))

    if args.command == "check":
        check(args.dataset_dir_a, args.dataset_dir_b)


if __name__ == "__main__":
    main(sys.argv[1:])
