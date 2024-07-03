import ast


class as_union:
    """
    In IntelliType,
    Union is Tuple[as_union, ...]

    ex)
        def function(intelli_typed: MyIntelliType[Tuple[as_union, int, str]])
    """

    pass


class as_union_def:
    """
    In IntelliType,
    We define Union as Tuple[as_union_def, ...]

    ex)
        class MyIntelliType(IntelliType, Tuple[as_union_def, int, str], Generic[T])
    """

    pass


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
                    and isinstance(elements[0], ast.Name)
                    and elements[-1].id == "as_union"
                ):
                    # Replace Tuple[..., as_union] with Union[...]
                    node.value.id = "Union"
                    if isinstance(node.slice, ast.Index):
                        node.slice.value = ast.Tuple(elts=elements[0:], ctx=ast.Load())
                    else:
                        node.slice = ast.Tuple(elts=elements[0:], ctx=ast.Load())
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

    if annotation_str.replace(" ", "").find("[as_union") == -1:
        annotation = annotation
    else:
        annotation_str_with_union = _transform_type_annotations(annotation_str)
        annotation_str_with_union = "annotation = " + annotation_str_with_union
        local_scope = {}
        exec(annotation_str_with_union, globals(), local_scope)
        annotation = local_scope["annotation"]

    return annotation


def handel_as_union_def(annotation):
    if str(annotation).find("as_union_def") != -1:
        annotation = str(annotation).replace("as_union_def", "as_union")
        annotation = _convert_annotation_to_str(annotation)
        annotation = handle_as_union(annotation)
    else:
        annotation = annotation

    return annotation
