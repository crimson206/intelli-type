import ast
from typing import Union  # noqa : F401

# It is to replace union as well. However, it is tricky to get the script env.


class TypeAnnotationTransformer(ast.NodeTransformer):
    def visit_Subscript(self, node):
        self.generic_visit(node)

        if isinstance(node.value, ast.Name) and node.value.id == "Tuple":
            if isinstance(node.slice, ast.Index):
                slice_value = node.slice.value
            else:
                slice_value = node.slice

            if isinstance(slice_value, ast.Tuple):
                elements = slice_value.elts
                if (
                    len(elements) > 1
                    and ast.unparse(elements[0]).find("as_union") != -1
                ):
                    # Replace Tuple[..., as_union] with Union[...]
                    node.value.id = "Union"
                    if isinstance(node.slice, ast.Index):
                        node.slice.value = ast.Tuple(elts=elements[1:], ctx=ast.Load())
                    else:
                        node.slice = ast.Tuple(elts=elements[1:], ctx=ast.Load())
        return node


def _transform_type_annotations(code: str) -> str:
    tree = ast.parse(code)
    transformer = TypeAnnotationTransformer()
    modified_tree = transformer.visit(tree)
    return ast.unparse(modified_tree)


def _convert_annotation_to_str(annotation) -> str:
    return str(annotation).replace("typing.", "").replace("__main__.", "")


def handle_as_union(annotation):

    if type(annotation) is not str:
        annotation_str = _convert_annotation_to_str(annotation)
    else:
        annotation_str = annotation

    if annotation_str.find("as_union") == -1:
        annotation = annotation
    else:
        annotation_str_with_union = _transform_type_annotations(annotation_str)
        annotation_str_with_union = "annotation = " + annotation_str_with_union
        local_scope = {}
        exec(annotation_str_with_union, local_scope)
        annotation = local_scope["annotation"]

    return annotation
