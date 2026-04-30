import ast
import re

def get_type_name(annotation) -> str:
    """Convert a type annotation node to a string."""
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
    return "any"

def get_default_value(default) -> str:
    """Convert a default value node to a string."""
    if isinstance(default, ast.Constant):
        return repr(default.value)
    if isinstance(default, ast.Name):
        return default.id
    return "..."

def build_curl(method: str, path: str, params: list) -> str:
    """Build a curl command from route info."""
    base = "http://localhost:8000"
    url = base + path

    # Replace path params like {user_id} with example values
    url = re.sub(r"\{(\w+)\}", lambda m: example_value(m.group(1), "path"), url)

    query_params = [p for p in params if p["location"] == "query"]
    body_params  = [p for p in params if p["location"] == "body"]

    if query_params:
        qs = "&".join(f"{p['name']}={example_value(p['name'], p['type'])}" for p in query_params)
        url += "?" + qs

    curl = f'curl -X {method} "{url}"'
    curl += ' \\\n  -H "Content-Type: application/json"'

    if body_params and method in ["POST", "PUT", "PATCH"]:
        body = {p["name"]: example_value(p["name"], p["type"]) for p in body_params}
        import json
        curl += f" \\\n  -d '{json.dumps(body)}'"

    return curl

def example_value(name: str, type_hint: str) -> str:
    """Return a realistic example value based on name and type."""
    name_lower = name.lower()
    if "email" in name_lower:    return "user@example.com"
    if "name" in name_lower:     return "John Doe"
    if "password" in name_lower: return "secret123"
    if "title" in name_lower:    return "My Title"
    if "id" in name_lower:       return "1"
    if "age" in name_lower:      return "25"
    if "url" in name_lower:      return "https://example.com"
    if type_hint == "bool":      return "true"
    if type_hint == "int":       return "1"
    if type_hint == "float":     return "1.0"
    return "example"

def parse_fastapi_code(code: str) -> list:
    """
    Parse a FastAPI Python file and extract all route definitions.
    Returns a list of dicts, each representing one endpoint.
    """
    routes = []
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return routes

    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue

        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue

            func = decorator.func
            # Match @app.get, @app.post, @router.get etc.
            if not isinstance(func, ast.Attribute):
                continue

            method = func.attr.upper()
            if method not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                continue

            # Extract path string from decorator argument
            path = ""
            if decorator.args:
                try:
                    path = ast.literal_eval(decorator.args[0])
                except:
                    path = "/unknown"

            # Extract docstring (written under the def line)
            docstring = ast.get_docstring(node) or ""

            # Extract parameters with types and defaults
            args = node.args
            all_args   = args.args
            defaults   = args.defaults
            # Pad defaults list to align with args
            pad = len(all_args) - len(defaults)
            defaults = [None] * pad + list(defaults)

            params = []
            for arg, default in zip(all_args, defaults):
                if arg.arg in ("self", "db", "request", "response"):
                    continue
                type_str = get_type_name(arg.annotation)
                default_str = get_default_value(default) if default else None

                # Guess location: path, query, or body
                if "{" + arg.arg + "}" in path:
                    location = "path"
                elif method in ["POST", "PUT", "PATCH"] and type_str not in ["int","float","bool","str","any"]:
                    location = "body"
                else:
                    location = "query"

                params.append({
                    "name": arg.arg,
                    "type": type_str,
                    "default": default_str,
                    "required": default is None,
                    "location": location,
                })

            # Extract return type
            return_type = get_type_name(node.returns)

            # Build the curl command
            curl = build_curl(method, path, params)

            routes.append({
                "method":      method,
                "path":        path,
                "function":    node.name,
                "description": docstring,
                "params":      params,
                "return_type": return_type,
                "curl":        curl,
            })

    return routes