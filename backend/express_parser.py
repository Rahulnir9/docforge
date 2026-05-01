import re
import json

def get_example_value(name: str, type_hint: str = "any"):
    name_lower = name.lower()
    if "email" in name_lower:    return "user@example.com"
    if "name" in name_lower:     return "John Doe"
    if "password" in name_lower: return "secret123"
    if "title" in name_lower:    return "My Title"
    if "id" in name_lower:       return 1
    if "age" in name_lower:      return 25
    if "url" in name_lower:      return "https://example.com"
    if "price" in name_lower:    return 9.99
    if "count" in name_lower:    return 10
    if "date" in name_lower:     return "2024-01-01"
    return "example"

def build_curl(method: str, path: str, body_fields: list, query_fields: list) -> str:
    base = "http://localhost:3000"
    url = base + path
    url = re.sub(r":(\w+)", lambda m: str(get_example_value(m.group(1))), url)

    if query_fields:
        qs = "&".join(f"{f}={get_example_value(f)}" for f in query_fields)
        url += "?" + qs

    curl = f'curl -X {method} "{url}"'
    curl += ' \\\n  -H "Content-Type: application/json"'

    if body_fields and method in ["POST", "PUT", "PATCH"]:
        body = {f: get_example_value(f) for f in body_fields}
        curl += f" \\\n  -d '{json.dumps(body)}'"

    return curl

def extract_jsdoc(lines: list, func_line_index: int) -> str:
    i = func_line_index - 1
    comment_lines = []
    while i >= 0:
        line = lines[i].strip()
        if line.endswith("*/"):
            j = i
            while j >= 0:
                l = lines[j].strip()
                comment_lines.insert(0, l)
                if l.startswith("/**") or l.startswith("/*"):
                    break
                j -= 1
            break
        elif line.startswith("//"):
            comment_lines.insert(0, line)
            i -= 1
            continue
        elif line == "":
            i -= 1
            continue
        else:
            break
        i -= 1

    if not comment_lines:
        return ""

    cleaned = []
    for l in comment_lines:
        l = re.sub(r"^/\*\*?", "", l).strip()
        l = re.sub(r"\*/$", "", l).strip()
        l = re.sub(r"^\*", "", l).strip()
        if l and not l.startswith("@"):
            cleaned.append(l)

    return " ".join(cleaned).strip()

def extract_req_body_fields(lines: list, start_index: int, end_index: int) -> list:
    fields = []
    body_pattern = re.compile(r"req\.body\.(\w+)")
    destructure_pattern = re.compile(r"const\s*\{([^}]+)\}\s*=\s*req\.body")

    for i in range(start_index, min(end_index, len(lines))):
        line = lines[i]
        for match in body_pattern.finditer(line):
            f = match.group(1)
            if f not in fields:
                fields.append(f)
        for match in destructure_pattern.finditer(line):
            for f in match.group(1).split(","):
                f = f.strip().split(":")[0].strip()
                if f and f not in fields:
                    fields.append(f)

    return fields

def extract_query_fields(lines: list, start_index: int, end_index: int) -> list:
    fields = []
    query_pattern = re.compile(r"req\.query\.(\w+)")
    destructure_pattern = re.compile(r"const\s*\{([^}]+)\}\s*=\s*req\.query")

    for i in range(start_index, min(end_index, len(lines))):
        line = lines[i]
        for match in query_pattern.finditer(line):
            f = match.group(1)
            if f not in fields:
                fields.append(f)
        for match in destructure_pattern.finditer(line):
            for f in match.group(1).split(","):
                f = f.strip().split(":")[0].strip()
                if f and f not in fields:
                    fields.append(f)

    return fields

def find_handler_end(lines: list, start_index: int) -> int:
    depth = 0
    for i in range(start_index, len(lines)):
        depth += lines[i].count("{") - lines[i].count("}")
        if depth <= 0 and i > start_index:
            return i
    return min(start_index + 30, len(lines))

def parse_express_code(code: str) -> list:
    routes = []
    lines = code.split("\n")

    # Matches app.get, router.get, Router.get etc — any variable name before the dot
    route_pattern = re.compile(
        r"(\w+)\.(get|post|put|delete|patch)\s*\(\s*['\"`]([^'\"` ]+)['\"`]",
        re.IGNORECASE
    )

    # Words that are definitely not route variables
    skip_names = {"console", "process", "module", "exports", "require", "Promise", "Object", "Array"}

    for i, line in enumerate(lines):
        for match in route_pattern.finditer(line):
            var_name = match.group(1)
            method   = match.group(2).upper()
            path     = match.group(3)

            # Skip obvious non-route patterns
            if var_name in skip_names:
                continue

            display_path = re.sub(r":(\w+)", r"{\1}", path)
            path_params  = re.findall(r":(\w+)", path)
            description  = extract_jsdoc(lines, i)
            handler_end  = find_handler_end(lines, i)
            body_fields  = extract_req_body_fields(lines, i, handler_end)
            query_fields = extract_query_fields(lines, i, handler_end)

            params = []
            for p in path_params:
                params.append({ "name": p, "type": "string", "default": None, "required": True,  "location": "path" })
            for q in query_fields:
                params.append({ "name": q, "type": "string", "default": None, "required": False, "location": "query" })
            for b in body_fields:
                params.append({ "name": b, "type": "any",    "default": None, "required": True,  "location": "body" })

            curl = build_curl(method, path, body_fields, query_fields)

            routes.append({
                "method":          method,
                "path":            display_path,
                "function":        f"{method.lower()}_{display_path.replace('/', '_').strip('_')}",
                "description":     description,
                "params":          params,
                "return_type":     "any",
                "response_schema": None,
                "curl":            curl,
                "framework":       "express"
            })

    return routes