#!/usr/bin/python3

import argparse
import csv
from glob import glob
from os.path import isdir, basename
from itertools import groupby
import spacy


def main():
    args = parse_args()

    files = []

    if args.input_dir:
        files = glob(f"{args.input_dir}/*.txt")

    if args.file:
        for f in args.file:
            files.append(f)

    parse_ner(files)


def parse_args() -> dict:
    parser = argparse.ArgumentParser(
        description="A script to scan text and output NER information"
    )
    parser.add_argument("-i", "--input_dir", type=dir_path)
    parser.add_argument("-o", "--output_dir", type=dir_path, nargs="?", const=".")
    parser.add_argument("-f", "--file", nargs="+")

    return parser.parse_args()


def dir_path(path: str) -> str:
    if isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"{path} is not a valid directory")


def parse_ner(files: list):
    nlp = spacy.load("en_core_web_sm")

    entity_maps = {}

    for file in files:
        with open(file) as f:
            file_root = basename(file).rpartition("-")[0]
            doc = nlp(f.read())

            entities = {
                key: list(set(map(lambda x: str(x), g)))
                for key, g in groupby(
                    sorted(doc.ents, key=lambda x: x.label_), lambda x: x.label_
                )
            }

            entity_maps.setdefault(file_root, {})
            entity_maps[file_root] = entity_maps[file_root] | entities

            write_results(entity_maps)


def write_results(entity_maps: dict):
    for file_root in entity_maps.keys():
        with open(f"./{file_root}.csv", "w") as ner_file:
            ner_dict = entity_maps[file_root]
            headers = ner_dict.keys()
            csvwriter = csv.DictWriter(ner_file, fieldnames=headers, delimiter="\t")
            csvwriter.writeheader()
            csvwriter.writerow(ner_dict)


if __name__ == "__main__":
    main()
