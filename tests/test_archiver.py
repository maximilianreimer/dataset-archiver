import json
import shutil
import tarfile
import tempfile
import unittest
from pathlib import Path

from  datasetarchiver import archiver


class TestArchiver(unittest.TestCase):
    def test_create_archive_same(self):
        source_dataset = Path('test_data/movies')
        with tempfile.TemporaryDirectory() as out_dir:
            out_dir = Path(out_dir)
            archive1 = archiver.archive_dataset(source_dataset, out_dir)
            archive2 = archiver.archive_dataset(source_dataset, out_dir)



            with tarfile.open(archive1, 'r') as archive_file1:
                with tarfile.open(archive2, 'r') as archive_file2:
                    self.assertListEqual(archive_file1.getnames(), archive_file2.getnames())

                    extracted1 = out_dir / 'extracted1'
                    archive_file1.extractall(extracted1)

                    extracted2 = out_dir / 'extracted2'
                    archive_file2.extractall(extracted2)

                    with open(extracted1 / 'meta.json', 'r') as f:
                        meta1 = json.load(f)

                    with open(extracted2/ 'meta.json', 'r') as f:
                        meta2 = json.load(f)

                    self.assertNotEqual(meta1['creation_date'], meta2['creation_date'])

                    del meta1['creation_date']
                    del meta2['creation_date']

                    self.assertDictEqual(meta1, meta2)

    def test_create_archive_copied(self):
        source_dataset = Path('test_data/movies')
        with tempfile.TemporaryDirectory() as out_dir:
            out_dir = Path(out_dir)
            copied_source_dataset = out_dir / source_dataset.name
            shutil.copytree(source_dataset, copied_source_dataset, copy_function=shutil.copy)


            archive1 = archiver.archive_dataset(copied_source_dataset, out_dir)
            archive2 = archiver.archive_dataset(source_dataset, out_dir)

            with tarfile.open(archive1, 'r') as archive_file1:
                with tarfile.open(archive2, 'r') as archive_file2:
                    self.assertListEqual(archive_file1.getnames(), archive_file2.getnames())

                    extracted1 = out_dir / 'extracted1'
                    archive_file1.extractall(extracted1)

                    extracted2 = out_dir / 'extracted2'
                    archive_file2.extractall(extracted2)

                    with open(extracted1 / 'meta.json', 'r') as f:
                        meta1 = json.load(f)

                    with open(extracted2 / 'meta.json', 'r') as f:
                        meta2 = json.load(f)

                    self.assertNotEqual(meta1['creation_date'], meta2['creation_date'])

                    del meta1['creation_date']
                    del meta2['creation_date']

                    self.assertDictEqual(meta1, meta2)


if __name__ == '__main__':
    unittest.main()
