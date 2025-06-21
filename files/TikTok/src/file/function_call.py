from os.path import basename, exists
from importlib.util import spec_from_file_location, module_from_spec
from ast import parse, ClassDef, FunctionDef, Expr, Constant


class library:
    def __init__(self, file_path):
        self.__file_path = file_path
        self.__file_name = basename(file_path)
        self.api = self.__analyze_structure__()  # 修改为公开属性

    def __analyze_structure__(self):
        file_content = self.__read_file__(self.__file_path)
        if (file_content is None):
            return None
        tree = parse(file_content)
        module = self.__load_module__(self.__file_path)
        results = [
            {
                "parent": None,
                "name": self.__file_name,
                "type": "Module",
                "pointer": None,
                "docstring": self.__extract_docstring__(tree)
            }
        ]
        self.__extract_module__(tree, results, "", module)
        return {self.__file_path: results}  # 使用完整的文件路径作为键

    def __extract_class__(self, class_node, results, parent_path, module):
        class_pointer = getattr(module, class_node.name)
        class_path = f"{parent_path}.{class_node.name}" if parent_path else class_node.name
        results.append({
            "parent": parent_path,
            "name": class_node.name,
            "type": "Class",
            "pointer": class_pointer,
            "docstring": self.__extract_docstring__(class_node)
        })
        for sub_node in class_node.body:
            match sub_node:
                case FunctionDef():
                    method_pointer = getattr(class_pointer, sub_node.name)
                    results.append(
                        {
                            "parent": class_path,
                            "name": sub_node.name,
                            "type": "Method",
                            "pointer": method_pointer,
                            "docstring": self.__extract_docstring__(sub_node)
                        }
                    )

    def __extract_docstring__(self, node):
        return (
            node.body[0].value.value
            if (
                node.body
                and type(node.body[0]) == Expr
                and type(node.body[0].value) == Constant
                and type(node.body[0].value.value) == str
            )
            else None
        )

    def __extract_function__(self, function_node, results, parent_path, module):
        function_pointer = getattr(module, function_node.name)
        results.append({
            "parent": parent_path,
            "name": function_node.name,
            "type": "Function",
            "pointer": function_pointer,
            "docstring": self.__extract_docstring__(function_node)
        })

    def __extract_module__(self, module_node, results, parent_path, module):
        for sub_node in module_node.body:
            match sub_node:
                case FunctionDef():
                    self.__extract_function__(
                        sub_node, results, parent_path, module)
                case ClassDef():
                    self.__extract_class__(
                        sub_node, results, parent_path, module)

    def __load_module__(self, file_path):
        spec = spec_from_file_location(self.__file_name, file_path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def __read_file__(self, file_path):
        file_data = None
        if (exists(file_path)):
            with open(file_path, "r", encoding="utf-8") as file:
                file_data = file.read()
        return file_data if (type(file_data) == str) else None


def __analyze_files__(file_paths):
    all_results = {}
    for file_path in sorted(file_paths):
        analyzer = library(file_path)
        file_structure = analyzer.api  # 直接访问 api 属性
        if (file_structure is not None):
            all_results.update(file_structure)
    return all_results


if (__name__ == "__main__"):
    from json import dumps
    file_paths = ["tiktok_mfa.py"]
    all_results = __analyze_files__(file_paths)
    function = all_results["tiktok_mfa.py"][1]["pointer"]("hello")
    print(dumps(function, indent=4, ensure_ascii=False))
