#!/usr/bin/python3

import argparse
from glob import glob
from os.path import isdir, isfile
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

    for file in files:
        with open(file) as f:
            doc = nlp(f.read())
            for ent in doc.ents:
                print(ent.text, ent.label_)


if __name__ == "__main__":
    main()
