from pathlib import Path

from anki.collection import Collection
from anki.models import NotetypeDict

MODEL_NAME = "Ordering"


def _load_file(file_name: str) -> str:
    return (Path(__file__).parent / "template" / file_name).read_text()


def get_or_create_model(collection: Collection, model_name: str = MODEL_NAME) -> tuple[NotetypeDict, bool]:
    """Fetch or create a new model with a given name."""
    if model := collection.models.by_name(model_name):
        return model, False

    model = collection.models.new(model_name)
    collection.models.add_template(model, collection.models.new_template(model_name))
    return model, True


def sync_model_templates(model: NotetypeDict) -> NotetypeDict:
    """Update a model with our latest templates."""
    model["css"] = _load_file("style.css")
    model["tmpls"][0]["qfmt"] = _load_file("front.html")
    model["tmpls"][0]["afmt"] = _load_file("back.html")
    return model


def sync_model_fields(collection: Collection, model: NotetypeDict) -> NotetypeDict:
    """Update a model with our expected fields."""
    expected_fields = ["Title", "Question", "Items", "Explanation"]
    existing_fields = {f["name"] for f in model["flds"]}

    for field_name in expected_fields:
        if field_name not in existing_fields:
            collection.models.add_field(model, collection.models.new_field(field_name))

    return model


def sync(collection: Collection, model_name: str = MODEL_NAME) -> NotetypeDict:
    """Create or update this note type in the given collection, returning the synced model."""
    model, created = get_or_create_model(collection, model_name)
    model = sync_model_templates(model)
    model = sync_model_fields(collection, model)

    if created:
        collection.models.add(model)
    else:
        collection.models.update_dict(model)

    return model
