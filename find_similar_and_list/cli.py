import os
import subprocess
import collections
import dataclasses
import argparse
import asyncio


@dataclasses.dataclass
class SimilarFiles(collections.UserList):
    data: list[str]

    @property
    def filename(self):
        return os.path.basename(self.data[0])

    @property
    def file(self):
        return self.data[0]

    def __init__(self, *args, **kwargs):
        self.data = [*args]
        super().__init__(**kwargs)

    def lines(self):
        count = len(self.data)
        first_file = self.data[0]
        size = subprocess.check_output(
                f'du -h "{first_file}"', shell=True).decode(
                        "utf-8").splitlines()[0].split()[0]
        lines = []
        lines.append(f"{count} files, size: {size}")
        lines += self.data
        return lines


async def get_list_of_similar_files():
    command = "find -type f -exec sha256sum {} + | sort | uniq --check-chars 10 --all-repeated=separate"
    out = subprocess.check_output(command, shell=True).decode(
            "utf-8").splitlines()
    without_hash = ["".join(row.split()[1:]) for row in out]
    similar_files: list[SimilarFiles] = []
    create_new = True
    for file in without_hash:
        if file == '':
            create_new = True
            continue
        if create_new:
            similar_files.append(SimilarFiles(file))
            create_new = False
        similar_files[-1].append(file)
    return similar_files


def ignore(files: SimilarFiles, ignore_list: list[str]) -> bool:
    for file in files:
        for filename in ignore_list:
            if filename in file:
                return True
    return False


async def read_ignore_file(filename) -> list[str]:
    if not filename:
        return []
    if not os.path.isfile(filename):
        raise TypeError
    with open(filename, "r", encoding="utf-8") as file:
        return file.read().splitlines()


def show(similar_files: list[SimilarFiles]):
    for i, files in enumerate(similar_files):
        for line in files.lines():
            print(line)
        if i != len(similar_files) - 1:
            print("")


def get_settings():
    parser = argparse.ArgumentParser()
    parser.add_argument("--files", type=str, nargs="+", help="Files to filter")
    parser.add_argument("--ignore-file", type=str, required=False)
    return parser.parse_args()


async def main_async():
    settings = get_settings()
    similar_files = await get_list_of_similar_files()
    ignore_list = await read_ignore_file(settings.ignore_file)
    if settings.files:
        filtered = [a for a in similar_files if a.filename in settings.files]
    else:
        filtered = similar_files
    filtered_ignore = [a for a in filtered if not ignore(a, ignore_list)]
    show(filtered_ignore)


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
