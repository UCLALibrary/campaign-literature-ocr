#!/usr/bin/python3

import argparse
import csv
from glob import glob
from os.path import isdir, basename
from itertools import groupby, zip_longest
from collections import defaultdict
import spacy


def main():
    args = parse_args()

    files = []

    if args.input_dir:
        files = glob(f"{args.input_dir}/*.txt")

    if args.file:
        for f in args.file:
            files.append(f)

    entity_dicts = parse_ner(files, args.model)
    write_entities(entity_dicts, args.output_dir)


def parse_args() -> dict:
    parser = argparse.ArgumentParser(
        description="A script to scan text and output NER information"
    )
    parser.add_argument("-i", "--input_dir", type=dir_path, nargs="?")
    parser.add_argument("-o", "--output_dir", type=dir_path, nargs="?", default=".")
    parser.add_argument("-f", "--file", nargs="+")
    parser.add_argument("-m", "--model", nargs="?", default="en_core_web_sm")

    return parser.parse_args()


def dir_path(path: str) -> str:
    if isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"{path} is not a valid directory")


def parse_ner(files: list, model: str) -> dict:
    """
    Given a list of file names, applies a NER model against each file.
    If the files follow a naming convention ending in '-[1-9]', the
    results will be merged into a single dict for this group of files.

    Example:

    1995-primary-01-1.txt
    1995-primary-01-2.txt

    Since the filename minus extension ends in '-1' and '-2', the
    entity dict is merged into a single entry with the key
    1995-primary-01

    Parameters:
        files (list): A list of file names including the path
        model (str): The name of the model to load and apply by spacy

    Returns:
        dict : A dict with a key for each file 'group' name, and value
        of a dict containing the file group entities
    """
    nlp = spacy.load(model)

    # entity_dicts is dict of:
    # key : file "group" name
    # value : dict of key : entity name, value: list of entity text
    entity_dicts = defaultdict(dict)

    for file in files:
        with open(file) as f:
            # A multi-page pdf can have a file for each 'page',
            # the naming convention consisting of a root filename
            # followed by '-.*?[0-9]' (dash followed by one or more digits)
            # We are interested in grouping these together, and only
            # interested in the root filename

            file_root = basename(file).rpartition("-")[0]
            doc = nlp(f.read())

            entities = create_entity_dict(doc.ents)

            temp_dict = entity_dicts[file_root]

            for k, v in entities.items():
                if k in temp_dict.keys():
                    temp_dict[k] += v
                else:
                    temp_dict[k] = v

            entity_dicts[file_root] = clean_data(temp_dict)

    return entity_dicts


def create_entity_dict(entities: tuple) -> dict:
    """
    Return a data structure more appropriate for our use of
    entity data.

    Parameters:
        entities (tuple): A tuple of spacy Span objects

    By default spacy returns a Doc containing a tuple of
    Span (https://spacy.io/api/span) objects with properies
    associated with the entity.

    To be able to manipulate groups of content based on the
    entity type, this is tranformed into a dict keyed by
    entity type with a value of a unique list of the associated
    text

    Default format of doc.ent:

    ent[0].label_ = "PERSON"
    ent[0].text = "Joe Bruin"
    ent[1].label_ = "PERSON"
    ent[1].text = "Jane Bruin"

    Returns:
        dict: Sample format of - { "PERSON" : ["Joe Bruin", "Jane Bruin"]}

    """
    return {
        key: list(set(map(lambda x: str(x), g)))
        for key, g in groupby(
            sorted(entities, key=lambda x: x.label_), lambda x: x.label_
        )
    }


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
