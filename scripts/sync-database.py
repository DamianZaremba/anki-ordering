#!/usr/bin/env python3
import sys
from pathlib import PosixPath

import click
from anki.collection import Collection

from helpers import get_or_create_model, sync_model_templates, sync_model_fields


def _create_or_update(collection_path: PosixPath, model_name: str) -> None:
    """Given a collection path, create or update our model."""
    collection = Collection(collection_path.as_posix())

    model, created = get_or_create_model(collection, model_name)
    model = sync_model_templates(model)
    model = sync_model_fields(collection, model)

    if created:
        print(f"Creating model: {model_name}")
        collection.models.add(model)
    else:
        print(f"Updating model: {model_name}")
        collection.models.update_dict(model)


def _auto_detect_profile(base_path: PosixPath) -> str | None:
    """Given a base Anki config path, detect a single profile name."""
    if profiles := [path.parent.stem for path in base_path.glob("*/collection.anki2")]:
        if len(profiles) == 1:
            return profiles[0]
        print(f"Found multiple profiles in {base_path}")
    return None


@click.command()
@click.option(
    "--path",
    type=click.Path(),
    default="~/Library/Application Support/Anki2",
    show_default=True,
    help="Path to the Anki storage location",
)
@click.option(
    "--profile",
    default=None,
    show_default=True,
    help="Profile to target",
)
@click.option(
    "--model-name",
    default="Ordering",
    show_default=True,
    help="Model name to use",
)
def main(path: str, profile: str, model_name: str) -> None:
    base_path = PosixPath(path).expanduser()
    if not base_path.is_dir():
        print(f"Config path does not exist: {base_path}")
        sys.exit(1)

    if not profile:
        if profile := _auto_detect_profile(base_path):
            print(f"Using auto detected profile: {profile}")
        else:
            print(f"Failed to auto detect profile in {base_path}")
            sys.exit(1)

    collection_path = base_path / profile / "collection.anki2"
    if not collection_path.is_file():
        print(f"Collection path does not appear valid: {collection_path}")
        sys.exit(1)

    _create_or_update(collection_path, model_name)


if __name__ == "__main__":
    main()
