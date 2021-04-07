import json
import shutil
import tarfile
import tempfile
import unittest
from pathlib import Path

from src.datasetarchiver import archiver
from src.datasetarchiver.archiver import archive_dataset, extract_dataset, md5


class TestArchiver(unittest.TestCase):
    def test_create_archive_same(self):
        source_dataset = Path("test_data/movies")
        with tempfile.TemporaryDirectory() as out_dir:
            out_dir = Path(out_dir)
            archive1 = archiver.archive_dataset(source_dataset, out_dir)
            archive2 = archiver.archive_dataset(source_dataset, out_dir)

            with tarfile.open(archive1, "r") as archive_file1:
                with tarfile.open(archive2, "r") as archive_file2:
                    self.assertListEqual(
                        archive_file1.getnames(), archive_file2.getnames()
                    )

                    extracted1 = out_dir / "extracted1"
                    archive_file1.extractall(extracted1)

                    extracted2 = out_dir / "extracted2"
                    archive_file2.extractall(extracted2)

                    with open(extracted1 / "meta.json", "r") as f:
                        meta1 = json.load(f)

                    with open(extracted2 / "meta.json", "r") as f:
                        meta2 = json.load(f)

                    self.assertNotEqual(meta1["creation_date"], meta2["creation_date"])

                    del meta1["creation_date"]
                    del meta2["creation_date"]

                    self.assertDictEqual(meta1, meta2)

    def test_create_archive_copied(self):
        source_dataset = Path("test_data/movies")
        with tempfile.TemporaryDirectory() as out_dir:
            out_dir = Path(out_dir)
            copied_source_dataset = out_dir / source_dataset.name
            shutil.copytree(
                source_dataset, copied_source_dataset, copy_function=shutil.copy
            )

            archive1 = archiver.archive_dataset(copied_source_dataset, out_dir)
            archive2 = archiver.archive_dataset(source_dataset, out_dir)

            with tarfile.open(archive1, "r") as archive_file1:
                with tarfile.open(archive2, "r") as archive_file2:
                    self.assertListEqual(
                        archive_file1.getnames(), archive_file2.getnames()
                    )

                    extracted1 = out_dir / "extracted1"
                    archive_file1.extractall(extracted1)

                    extracted2 = out_dir / "extracted2"
                    archive_file2.extractall(extracted2)

                    with open(extracted1 / "meta.json", "r") as f:
                        meta1 = json.load(f)

                    with open(extracted2 / "meta.json", "r") as f:
                        meta2 = json.load(f)

                    self.assertNotEqual(meta1["creation_date"], meta2["creation_date"])

                    del meta1["creation_date"]
                    del meta2["creation_date"]
                    self.assertDictEqual(meta1, meta2)

    def test_create_archive_renamed(self):
        source_dataset = Path("test_data/movies")
        with tempfile.TemporaryDirectory() as out_dir:
            out_dir = Path(out_dir)
            copied_source_dataset = out_dir / source_dataset.name
            shutil.copytree(
                source_dataset, copied_source_dataset, copy_function=shutil.copy
            )
            new_name = copied_source_dataset.parent / "test"
            copied_source_dataset.rename(new_name)
            copied_source_dataset = new_name

            archive1 = archiver.archive_dataset(copied_source_dataset, out_dir)
            archive2 = archiver.archive_dataset(source_dataset, out_dir)

            with tarfile.open(archive1, "r") as archive_file1:
                with tarfile.open(archive2, "r") as archive_file2:
                    self.assertListEqual(
                        archive_file1.getnames(), archive_file2.getnames()
                    )

                    extracted1 = out_dir / "extracted1"
                    archive_file1.extractall(extracted1)

                    extracted2 = out_dir / "extracted2"
                    archive_file2.extractall(extracted2)

                    with open(extracted1 / "meta.json", "r") as f:
                        meta1 = json.load(f)

                    with open(extracted2 / "meta.json", "r") as f:
                        meta2 = json.load(f)

                    self.assertNotEqual(meta1["creation_date"], meta2["creation_date"])

                    del meta1["creation_date"]
                    del meta2["creation_date"]
                    self.assertDictEqual(meta1, meta2)

    def test_extract(self):
        source_dataset = Path("test_data/movies")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)

            archive_path = archive_dataset(source_dataset, temp_dir)
            extracted_dataset = extract_dataset(archive_path, temp_dir)

            source_files = map(
                lambda path: path.relative_to(source_dataset), source_dataset.rglob("*")
            )
            extracted_files = map(
                lambda path: path.relative_to(extracted_dataset),
                extracted_dataset.rglob("*"),
            )

            sorted_source_files = sorted(source_files, key=lambda path: str(path))
            sorted_extracted_files = sorted(extracted_files, key=lambda path: str(path))

            self.assertListEqual(
                [str(file) for file in sorted_source_files],
                [str(file) for file in sorted_extracted_files],
            )

            for source_file, extracted_file in zip(
                sorted_source_files, sorted_extracted_files
            ):
                abs_source_file = source_dataset / source_file
                abs_extracted_file = extracted_dataset / extracted_file
                if abs_extracted_file.is_dir():
                    continue
                self.assertEqual(md5(abs_source_file), md5(abs_extracted_file))


if __name__ == "__main__":
    unittest.main()
