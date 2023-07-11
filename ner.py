#!/usr/bin/python3

import argparse
import csv
from glob import glob
from os.path import isdir, basename
from itertools import groupby, zip_longest
import spacy


def main():
    args = parse_args()

    files = []

    if args.input_dir:
        files = glob(f"{args.input_dir}/*.txt")

    if args.file:
        for f in args.file:
            files.append(f)

    entity_dicts = parse_ner(files)
    write_entities(entity_dicts, args.output_dir)


def parse_args() -> dict:
    parser = argparse.ArgumentParser(
        description="A script to scan text and output NER information"
    )
    parser.add_argument("-i", "--input_dir", type=dir_path, nargs="?")
    parser.add_argument("-o", "--output_dir", type=dir_path, nargs="?", default=".")
    parser.add_argument("-f", "--file", nargs="+")

    return parser.parse_args()


def dir_path(path: str) -> str:
    if isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"{path} is not a valid directory")


def parse_ner(files: list) -> dict:
    nlp = spacy.load("en_core_web_sm")

    entity_dicts = {}

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

            entity_dicts.setdefault(file_root, {})
            temp_dict = entity_dicts[file_root]

            for k, v in entities.items():
                if k in temp_dict.keys():
                    temp_dict[k] += v
                else:
                    temp_dict[k] = v

            entity_dicts[file_root] = clean_data(temp_dict)

    return entity_dicts


def clean_data(entity_dict: dict) -> dict:
    e_to_keep = ["PERSON", "ORG", "GPE", "NORP"]
    entity_dict = {k: v for k, v in entity_dict.items() if k in e_to_keep}

    for k in entity_dict.keys():
        entity_dict[k] = [" ".join(val.splitlines()) for val in entity_dict[k]]
    return entity_dict


def write_entities(entity_dicts: dict, output_dir: str):
    for file_root in entity_dicts.keys():
        with open(f"{output_dir}/{file_root}.tsv", "w") as ner_file:
            ner_dict = entity_dicts[file_root]
            output(ner_file, ner_dict)


def output(output_loc: str, output_dict: dict):
    csvwriter = csv.writer(output_loc, delimiter="\t")
    csvwriter.writerow(output_dict.keys())
    csvwriter.writerows(zip_longest(*output_dict.values()))


if __name__ == "__main__":
    main()
