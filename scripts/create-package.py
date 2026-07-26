#!/usr/bin/env python3
import json
import tempfile
from pathlib import PosixPath

import click
from anki.collection import Collection, ExportAnkiPackageOptions, DeckIdLimit
from anki.models import NotetypeDict
from anki.notes import Note

from helpers import get_or_create_model, sync_model_templates, sync_model_fields


def _create_note(collection: Collection, model: NotetypeDict) -> Note:
    """Generate an example note."""
    note = collection.new_note(model)
    note["Title"] = "Example Ordering"
    note["Question"] = "Put these steps in the correct order"
    note["Items"] = json.dumps(["Wake up", "Make coffee", "Drink coffee", "Leave the house"])
    note["Explanation"] = "You need to be awake before you can make coffee."
    return note


def _create_package(path: PosixPath, model_name: str) -> None:
    """Create a new package file at the given path."""
    with tempfile.NamedTemporaryFile(suffix="anki2") as f:
        collection = Collection(f.name)

        model, _ = get_or_create_model(collection, model_name)
        model = sync_model_templates(model)
        model = sync_model_fields(collection, model)
        collection.models.add(model)

        deck_id = collection.decks.id("Ordering Example")
        collection.add_note(_create_note(collection, model), deck_id)

        collection.export_anki_package(
            out_path=path.absolute().as_posix(),
            options=ExportAnkiPackageOptions(with_scheduling=False, with_media=True, legacy=True),
            limit=DeckIdLimit(deck_id=deck_id),
        )


@click.command()
@click.option(
    "--path",
    type=click.Path(),
    default="ordering.apkg",
    show_default=True,
    help="Output path for the package file",
)
@click.option(
    "--model-name",
    default="Ordering",
    show_default=True,
    help="Model name to use",
)
def main(path: str, model_name: str) -> None:
    export_path = PosixPath(path)
    print(f"Creating package at {export_path}")
    _create_package(export_path, model_name)


if __name__ == "__main__":
    main()
