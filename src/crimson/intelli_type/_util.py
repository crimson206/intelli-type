from pydantic import create_model, ConfigDict


def _create_base_model(annotation, cls_name):
    _BaseModel = create_model(
        f"{cls_name}Props",
        data=(annotation, ...),
        __config__=ConfigDict(arbitrary_types_allowed=True),
    )
    return _BaseModel
