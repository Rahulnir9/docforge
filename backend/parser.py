import ast
import re
import json

def get_type_name(annotation) -> str:
    if annotation is None:
        return "any"
    if isinstance(annotation, ast.Name):
        return annotation.id
    if isinstance(annotation, ast.Subscript):
        outer = get_type_name(annotation.value)
        inner = get_type_name(annotation.slice)
        return f"{outer}[{inner}]"
    if isinstance(annotation, ast.Attribute):
        return annotation.attr
    if isinstance(annotation, ast.Constant):
        return str(annotation.value)
    if isinstance(annotation, ast.Tuple):
        return ", ".join(get_type_name(e) for e in annotation.elts)
    return "any"

def get_default_value(default) -> str:
    if default is None:
        return None
    if isinstance(default, ast.Constant):
        return repr(default.value)
    if isinstance(default, ast.Name):
        return default.id
    if isinstance(default, ast.Call):
        if default.args:
            arg = default.args[0]
            if isinstance(arg, ast.Constant) and arg.value is not ...:
                return repr(arg.value)
        for kw in default.keywords:
            if kw.arg == "default" and isinstance(kw.value, ast.Constant):
                return repr(kw.value.value)
    return None

def example_value(name: str, type_hint: str):
    name_lower = name.lower()
    if "email" in name_lower:    return "user@example.com"
    if "name" in name_lower:     return "John Doe"
    if "password" in name_lower: return "secret123"
    if "title" in name_lower:    return "My Title"
    if "id" in name_lower:       return 1
    if "age" in name_lower:      return 25
    if "url" in name_lower:      return "https://example.com"
    if "price" in name_lower:    return 9.99
    if "total" in name_lower:    return 49.99
    if "count" in name_lower:    return 10
    if "date" in name_lower:     return "2024-01-01"
    if "phone" in name_lower:    return "+1234567890"
    if "address" in name_lower:  return "123 Main St"
    if "city" in name_lower:     return "New York"
    if "zip" in name_lower:      return "10001"
    if "status" in name_lower:   return "active"
    if "token" in name_lower:    return "eyJhbGciOiJIUzI1NiJ9..."
    if type_hint == "bool":      return True
    if type_hint == "int":       return 1
    if type_hint == "float":     return 1.0
    if type_hint == "str":       return "string"
    return "example"

def build_example_from_model(model_name: str, models: dict, visited: set = None) -> dict:
    if visited is None:
        visited = set()
    if model_name not in models:
        return {}
    if model_name in visited:
        return {"$ref": model_name}
    visited.add(model_name)

    result = {}
    for field_name, field_info in models[model_name].items():
        field_type = field_info["type"]
        is_optional = field_info.get("optional", False)

        # Optional[X] with None default
        opt_match = re.match(r"Optional\[(\w+)\]", field_type)
        if opt_match:
            inner = opt_match.group(1)
            if is_optional:
                result[field_name] = None
                continue
            field_type = inner

        # List[X]
        list_match = re.match(r"List\[(\w+)\]", field_type)
        if list_match:
            inner = list_match.group(1)
            if inner in models:
                result[field_name] = [build_example_from_model(inner, models, visited.copy())]
            else:
                result[field_name] = [example_value(field_name, inner)]
            continue

        # Nested model
        if field_type in models:
            result[field_name] = build_example_from_model(field_type, models, visited.copy())
            continue

        result[field_name] = example_value(field_name, field_type)

    return result

def parse_pydantic_models(tree) -> dict:
    models = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        is_pydantic = any(
            (isinstance(b, ast.Name) and b.id == "BaseModel") or
            (isinstance(b, ast.Attribute) and b.attr == "BaseModel")
            for b in node.bases
        )
        if not is_pydantic:
            continue

        fields = {}
        for item in node.body:
            if not isinstance(item, ast.AnnAssign):
                continue
            if not isinstance(item.target, ast.Name):
                continue

            field_name = item.target.id
            field_type = get_type_name(item.annotation)
            default = get_default_value(item.value) if item.value else None
            required = item.value is None
            is_optional = field_type.startswith("Optional[") or default == "None"

            fields[field_name] = {
                "type": field_type,
                "default": default,
                "required": required,
                "optional": is_optional,
            }
        if fields:
            models[node.name] = fields

    return models

def parse_router_prefixes(tree) -> dict:
    prefixes = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not isinstance(node.value, ast.Call):
            continue
        func = node.value.func
        func_name = ""
        if isinstance(func, ast.Name):
            func_name = func.id
        elif isinstance(func, ast.Attribute):
            func_name = func.attr

        if func_name != "APIRouter":
            continue

        prefix = ""
        for kw in node.value.keywords:
            if kw.arg == "prefix" and isinstance(kw.value, ast.Constant):
                prefix = kw.value.value

        for target in node.targets:
            if isinstance(target, ast.Name):
                prefixes[target.id] = prefix

    return prefixes

def get_tags_from_decorator(decorator) -> list:
    """Extract tags=["Users"] from decorator kwargs."""
    for kw in decorator.keywords:
        if kw.arg == "tags":
            if isinstance(kw.value, ast.List):
                return [
                    elt.value for elt in kw.value.elts
                    if isinstance(elt, ast.Constant)
                ]
    return []

def get_response_model_from_decorator(decorator) -> str:
    for kw in decorator.keywords:
        if kw.arg == "response_model":
            return get_type_name(kw.value)
    return ""

def resolve_response_schema(return_type: str, response_model: str, models: dict) -> dict:
    effective_type = response_model if response_model else return_type

    if not effective_type or effective_type in ("any", "None", ""):
        return None

    # List[Model]
    list_match = re.match(r"List\[(\w+)\]", effective_type)
    if list_match:
        inner = list_match.group(1)
        if inner in models:
            example = build_example_from_model(inner, models)
            return {
                "type": "array",
                "inner_model": inner,
                "fields": models[inner],
                "example": [example]
            }
        return {"type": "array", "example": []}

    # Optional[Model]
    opt_match = re.match(r"Optional\[(\w+)\]", effective_type)
    if opt_match:
        effective_type = opt_match.group(1)

    # Pydantic model
    if effective_type in models:
        example = build_example_from_model(effective_type, models)
        return {
            "type": "object",
            "model": effective_type,
            "fields": models[effective_type],
            "example": example
        }

    # Primitives
    primitive_map = {
        "str":   {"type": "string",  "example": "string"},
        "int":   {"type": "integer", "example": 1},
        "float": {"type": "number",  "example": 1.0},
        "bool":  {"type": "boolean", "example": True},
        "dict":  {"type": "object",  "example": {}},
        "list":  {"type": "array",   "example": []},
    }
    if effective_type in primitive_map:
        return primitive_map[effective_type]

    return {"type": effective_type, "example": None}

def build_curl(method: str, full_path: str, params: list, body_example: dict = None) -> str:
    base = "http://localhost:8000"
    url = base + full_path

    url = re.sub(r"\{(\w+)\}", lambda m: str(example_value(m.group(1), "path")), url)

    query_params = [p for p in params if p["location"] == "query"]
    if query_params:
        qs = "&".join(
            f"{p['name']}={example_value(p['name'], p['type'])}"
            for p in query_params
        )
        url += "?" + qs

    curl = f'curl -X {method} "{url}"'
    curl += ' \\\n  -H "Content-Type: application/json"'

    if body_example and method in ["POST", "PUT", "PATCH"]:
        # Always use full schema example in curl body
        curl += f" \\\n  -d '{json.dumps(body_example, indent=2)}'"

    return curl

def parse_fastapi_code(code: str) -> list:
    routes = []
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return routes

    models = parse_pydantic_models(tree)
    router_prefixes = parse_router_prefixes(tree)

    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue

        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue

            func = decorator.func
            if not isinstance(func, ast.Attribute):
                continue

            method = func.attr.upper()
            if method not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                continue

            # Support any variable name: app, router, api, v1 etc
            var_name = ""
            if isinstance(func.value, ast.Name):
                var_name = func.value.id

            path = ""
            if decorator.args:
                try:
                    path = ast.literal_eval(decorator.args[0])
                except:
                    path = "/unknown"

            # Apply router prefix
            prefix = router_prefixes.get(var_name, "")
            full_path = (prefix.rstrip("/") + "/" + path.lstrip("/")).rstrip("/")
            if not full_path.startswith("/"):
                full_path = "/" + full_path

            # Tags from decorator — used for grouping
            tags = get_tags_from_decorator(decorator)

            # Docstring fallback
            docstring = ast.get_docstring(node) or "No description available."

            # Response model
            response_model = get_response_model_from_decorator(decorator)

            # Parse parameters
            args = node.args
            all_args = args.args
            defaults = args.defaults
            pad = len(all_args) - len(defaults)
            defaults = [None] * pad + list(defaults)

            params = []
            body_example = {}

            for arg, default in zip(all_args, defaults):
                if arg.arg in ("self", "db", "request", "response", "background_tasks"):
                    continue

                type_str = get_type_name(arg.annotation)
                default_str = get_default_value(default)

                # Location detection
                if "{" + arg.arg + "}" in full_path:
                    location = "path"
                elif type_str in models:
                    location = "body"
                elif re.match(r"List\[", type_str):
                    inner = re.sub(r"List\[(\w+)\]", r"\1", type_str)
                    location = "body" if inner in models else "query"
                elif re.match(r"Optional\[", type_str):
                    inner = re.sub(r"Optional\[(\w+)\]", r"\1", type_str)
                    location = "body" if inner in models else "query"
                elif method in ["POST", "PUT", "PATCH"] and type_str not in ["int", "float", "bool", "str", "any"]:
                    location = "body"
                else:
                    location = "query"

                # Build full body example from Pydantic model
                if location == "body" and type_str in models:
                    body_example = build_example_from_model(type_str, models)

                params.append({
                    "name": arg.arg,
                    "type": type_str,
                    "default": default_str,
                    "required": default is None,
                    "location": location,
                })

            return_type = get_type_name(node.returns)
            response_schema = resolve_response_schema(return_type, response_model, models)
            curl = build_curl(method, full_path, params, body_example)

            # Group priority: tags > prefix > path segment
            if tags:
                group = tags[0]
            elif prefix:
                group = prefix.strip("/").split("/")[0]
            else:
                parts = full_path.strip("/").split("/")
                group = parts[0].replace("{", "").replace("}", "") if parts else "general"

            routes.append({
                "method":          method,
                "path":            full_path,
                "function":        node.name,
                "description":     docstring,
                "params":          params,
                "return_type":     return_type,
                "response_schema": response_schema,
                "curl":            curl,
                "group":           group,
                "tags":            tags,
            })

    return routes