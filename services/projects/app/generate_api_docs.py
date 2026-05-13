import json
import urllib.error
import urllib.request
from pathlib import Path

OPENAPI_URL = "http://localhost:5000/openapi.json"
OPENAPI_PATH = Path("services/projects/docs/openapi.json")
MARKDOWN_PATH = Path("services/projects/docs/API.md")


def fetch_openapi_spec():
    """Fetch OpenAPI JSON from the running Flask container.

    return: Parsed OpenAPI specification dictionary.
    raises RuntimeError: If the Flask server cannot be reached.
    """
    try:
        with urllib.request.urlopen(OPENAPI_URL, timeout=5) as response:
            data = response.read()
            print(f"Fetched OpenAPI spec from {OPENAPI_URL}")
            return json.loads(data)

    except urllib.error.URLError as exc:
        raise RuntimeError(
            "\nCould not fetch the OpenAPI spec.\n\n"
            f"Tried: {OPENAPI_URL}\n\n"
            "Make sure the projects Flask container is running and that the port is exposed.\n\n"
            "Example:\n"
            "  docker compose up projects\n\n"
            "Then try again:\n"
            "  python scripts/generate_api_docs.py\n"
        ) from exc


def save_openapi_json(spec):
    """Save OpenAPI spec to docs/openapi.json.

    param spec: Parsed OpenAPI specification dictionary.
    return: None.
    """
    OPENAPI_PATH.parent.mkdir(parents=True, exist_ok=True)
    OPENAPI_PATH.write_text(json.dumps(spec, indent=2), encoding="utf-8")
    print("Saved docs/openapi.json")


def generate_api_md(spec):
    """Generate a human-readable API.md from OpenAPI spec.

    param spec: Parsed OpenAPI specification dictionary.
    return: None.
    """
    title = spec["info"]["title"]
    version = spec["info"]["version"]
    paths = spec["paths"]

    lines = [
        f"# {title}",
        "",
        f"Version: `{version}`",
        "",
        "Base URL:",
        "",
        "```text",
        "/api",
        "```",
        "",
        "Swagger UI:",
        "",
        "```text",
        "/docs",
        "```",
        "",
        "## Authentication",
        "",
        "Project endpoints require:",
        "",
        "```text",
        "X-User-ID: <user-id>",
        "```",
        "",
        "## Endpoints",
        "",
        "| Method | Path | Description | Auth |",
        "|---|---|---|---|",
    ]

    for path, methods in paths.items():
        for method, details in methods.items():
            if method == "parameters":
                continue

            summary = details.get("summary", "")
            parameters = details.get("parameters", [])

            requires_auth = any(parameter.get("name") == "X-User-ID" for parameter in parameters)
            auth = "Yes" if requires_auth else "No"

            lines.append(f"| {method.upper()} | `{path}` | {summary} | {auth} |")

    lines.extend(
        [
            "",
            "## Error responses",
            "",
            "| Status | Meaning |",
            "|---|---|",
            "| 400 | Bad request, such as missing `X-User-ID` |",
            "| 404 | Resource not found |",
            "| 422 | Request body validation failed |",
            "",
        ]
    )

    MARKDOWN_PATH.parent.mkdir(parents=True, exist_ok=True)
    MARKDOWN_PATH.write_text("\n".join(lines), encoding="utf-8")
    print("Saved docs/API.md")


def main():
    """Generate OpenAPI JSON and Markdown API documentation.

    return: None.
    """
    try:
        spec = fetch_openapi_spec()
    except RuntimeError as exc:
        print(exc)
        return

    save_openapi_json(spec)
    generate_api_md(spec)

    print("\nAPI documentation generated successfully")


if __name__ == "__main__":
    main()
