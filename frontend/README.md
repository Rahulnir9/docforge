# DocForge

Upload your API codebase and get instant, interactive documentation — no setup, no config, no manual writing.

**Live demo:** https://your-demo-link-here.vercel.app

---

## The problem

You finish building an API. Now someone asks for the docs.

You either spend 2 hours writing them manually in Notion or Markdown, or you tell them to clone the repo and run the server just to see the `/docs` page. Neither is great.

DocForge fixes this. Upload your file, get a shareable docs page in under 10 seconds.

---

## What it does

Drop in a `.py`, `.js`, `.ts`, or `.zip` file. DocForge parses every route, extracts parameters and types, reads your docstrings, and renders everything into a clean interactive docs page.

No AI. No API calls. Pure static analysis — it reads your code the same way a compiler would.

**For every endpoint you get:**
- Method badge, path, and description from your docstring
- Full parameter table with types, locations (path / query / body), required status, and defaults
- Response schema with field names and types extracted from your Pydantic models
- Realistic example response JSON built from your actual model definitions
- A ready-to-run curl command with real example values — not placeholders

**Other features:**
- Routes grouped by prefix or `tags=[]` decorator argument
- Stats bar showing total endpoints broken down by method
- Search across paths, descriptions, and tags
- Filter by HTTP method
- Export the full docs as a Markdown file — paste it straight into your README

---

## Supported frameworks

| Framework | File types | Route style |
|-----------|-----------|-------------|
| FastAPI | `.py`, `.zip` | `@app.get()`, `@router.post()`, any variable name |
| Express.js | `.js`, `.ts`, `.zip` | `app.get()`, `router.post()`, any variable name |

---

## Stack

- **Frontend** — React + Vite
- **Backend** — FastAPI + Python
- **Parsing** — Python `ast` module (zero external dependencies for parsing)
- **Deployment** — Vercel (frontend) + Render (backend)

---

## How the parser works

Most tools like this call an AI API and hope for the best. DocForge uses Python's built-in `ast` module to parse code into a syntax tree, then walks the tree looking for decorated functions.

For FastAPI files it:
1. Finds all Pydantic `BaseModel` subclasses and maps their fields
2. Detects `APIRouter(prefix="/something")` assignments and stores the prefix per variable name
3. Walks every function, finds HTTP method decorators, extracts the path, parameters with type annotations, docstring, `response_model`, and `tags`
4. Resolves nested models recursively to build realistic example JSON
5. Generates curl commands with context-aware example values — if a param is named `email` it uses `user@example.com`, not `"example"`

For Express files it uses regex to find route definitions on any variable name, then scans the handler body for `req.body`, `req.query`, and `req.params` patterns including destructuring syntax.

---

## Running locally

**Backend**

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs on `http://localhost:8000`

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`

---

## Project structure
docforge/
├── backend/
│   ├── main.py              # FastAPI server, /generate endpoint
│   ├── code_parser.py       # AST-based FastAPI parser
│   ├── express_parser.py    # Regex-based Express.js parser
│   └── requirements.txt
└── frontend/
└── src/
├── App.jsx          # Upload screen
└── DocsView.jsx     # Interactive docs renderer

---

## Things I learned building this

Writing a parser from scratch forces you to understand how Python actually reads code. The `ast` module turns source code into a tree of objects — every function, decorator, argument, and type annotation becomes a node you can inspect and traverse. Once you understand that, extracting structured data from code becomes straightforward.

The hardest part was resolving nested Pydantic models recursively without hitting infinite loops on circular references. The fix was tracking visited model names in a set and bailing out if we detect a cycle.

The Express parser was a different challenge — JavaScript has no type annotations so there is nothing to extract except what the developer explicitly accesses via `req.body.fieldName` or destructuring. Regex scanning the handler body for those patterns turned out to work surprisingly well in practice.

---

## What's next

- Try it → request builder (send real requests from the browser, see live responses)
- Share as link (encode docs into a compressed URL, no hosting needed)
- OpenAPI JSON export
- TypeScript type extraction for Express routes
