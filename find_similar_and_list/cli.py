import os
import subprocess


class File:
    path: str
    hashsum: str

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)


def find_all_files() -> list[str]:
    return subprocess.check_output(
            "find -type f", shell=True).decode("utf-8").splitlines()


def get_file_hash(path) -> str:
    return subprocess.check_output(
            f'sha512sum "{path}"', shell=True).decode("utf-8")


def sort_similar_files(files: list[File]) -> list[list[File]]:
    hashsums = [files[0].hashsum]
    result = []
    similar_files = []
    for file in files:
        if file.hashsum == hashsums[-1]:
            similar_files.append(file)
        else:
            result.append(similar_files.copy())
            similar_files.clear()
            similar_files.append(file)
        hashsums.append(file.hashsum)
    return result


def filter_ignore(filenames: list[str],
                  ignore_filenames: list[str]) -> list[str]:
    result = []
    for filename in filenames:
        skip = False
        for ignore_filename in ignore_filenames:
            if ignore_filename in filename:
                skip = True
        if not skip:
            result.append(filename)
    return result


def output(similar_files_list: list) -> list[str]:
    result = []
    for similar_files in similar_files_list:
        lines = [file.path for file in similar_files]
        result += [*lines, ""]
    return result


def read_ignore_file(filename):
    if not os.path.isfile(filename):
        raise TypeError
    with open(filename, "r", encoding="utf-8") as file:
        return file.readlines()


def main():
    all_files = find_all_files()
    filtered_files = filter_ignore(all_files, read_ignore_file("./.gitignore"))
    hashsums_with_filenames = [get_file_hash(path) for path in filtered_files]
    hashsums = [x.split()[0] for x in hashsums_with_filenames]
    files = [File(path=a, hashsum=b) for a, b in zip(all_files, hashsums)]
    files.sort(key=lambda x: x.hashsum)
    similar_files = sort_similar_files(files)
    similar_files_filtered = [x for x in similar_files if len(x) > 1]
    _ = [print(line) for line in output(similar_files_filtered)]


if __name__ == "__main__":
    main()
