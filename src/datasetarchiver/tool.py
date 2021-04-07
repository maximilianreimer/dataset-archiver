import argparse
import json
import sys

from pathlib import Path

from datasetarchiver.archiver import archive_dataset, extract_dataset


def is_valid_file(arg):
    path = Path(arg)
    if not path.exists():
        raise argparse.ArgumentTypeError("The folder %s does not exist!" % arg)
    else:
        return path


def create():
    pass


def extract():
    pass


def main(args=None):
    args = args if args is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(
        "Utility to crate dataset archive and store additional meta data."
        "The resulting dataset archive will contain a meta.json containing a"
        "unique md5 checksum of the dataset as well as other useful information"
    )
    sub_parsers = parser.add_subparsers(dest="command")

    create_parser = sub_parsers.add_parser(
        "create",
        help="Creates a archive containing the dataset and meta data."
        "If the dataset folder contains a file 'meta.json' this "
        "will be added to the meta data. "
        "The resulting meta data contains: "
        "    1. The meta data in the meta.json in the dataset path"
        "    2. Adds and updated values from provided meta-data"
        "    3. This script will add:   "
        "        * md5checksum to the compressed data"
        "        * creation_data in the iso format"
        "        * name derived from folder name if not already in 1. or 2.",
    )

    create_parser.add_argument(
        "--dataset_dir",
        type=is_valid_file,
        required=True,
        help="Directory of the dataset",
    )
    create_parser.add_argument(
        "--meta_data",
        type=str,
        default=None,
        required=False,
        help="A string following the json format, used to updated the values of"
        " the meta.json.",
    )
    create_parser.add_argument(
        "--archives_path",
        type=str,
        required=True,
        help="The directory to write the resulting archive to",
    )

    extract_parser = sub_parsers.add_parser(
        "extract", help="Extracts the data from a previously created dataset archive"
    )
    extract_parser.add_argument(
        "--dataset_archive",
        type=is_valid_file,
        required=True,
        help="The archive file created by the create command",
    )
    extract_parser.add_argument(
        "--extract_path",
        type=is_valid_file,
        required=True,
        help="The folder to extract the archive to. "
        "Note that that inside of this folder a new folder is created named like "
        "the 'name' property of the meta data. This operation fails if a dataset "
        "with same name alredy exits",
    )
    if len(args) == 0:
        parser.print_help()
        return
    args = parser.parse_args(args)

    if args.command == "create":
        archive_dataset(
            args.dataset_dir, args.archives_path, json.loads(args.meta_data)
        )
    if args.command == "extract":
        extract_dataset(args.dataset_archive, args.extract_path)
