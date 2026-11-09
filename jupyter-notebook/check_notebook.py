"""Execute a notebook from a fresh kernel and run the public checks."""
import argparse
from pathlib import Path
import sys

import nbformat
from nbclient import NotebookClient


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebook", type=Path)
    parser.add_argument("--output", type=Path, help="optional executed notebook artifact")
    args = parser.parse_args(argv)
    source = args.notebook.resolve()
    if args.output is not None and args.output.resolve() == source:
        parser.error("output must differ from the source notebook")
    notebook = None
    try:
        notebook = nbformat.read(source, as_version=4)
        nbformat.validate(notebook)
        checks = (Path(__file__).parent / "checks.py").read_text(encoding="utf-8")
        notebook.cells.append(nbformat.v4.new_code_cell(checks + "\ncheck_summary(summarize)\n"))
        client = NotebookClient(notebook, timeout=60, kernel_name="python3", resources={"metadata": {"path": str(source.parent)}})
        client.execute()
    except Exception as exc:
        print(f"Notebook check failed: {exc}", file=sys.stderr)
        return 1
    finally:
        if notebook is not None and args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            nbformat.write(notebook, args.output)
    print("OK: all 5 public checks passed in a fresh kernel")
    return 0


if __name__ == "__main__":
    sys.exit(main())
