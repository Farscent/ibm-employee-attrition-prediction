"""Execute the project notebook in a fresh kernel and save it only on success."""
import asyncio
import os
from pathlib import Path
import sys

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "OmniCampus25UGM_FarhanAP.ipynb"


def main():
    # Keep Jupyter's generated state inside the ignored project cache.
    cache = ROOT / ".cache"
    for variable, directory in {
        "IPYTHONDIR": cache / "ipython",
        "JUPYTER_RUNTIME_DIR": cache / "jupyter",
        "MPLCONFIGDIR": cache / "matplotlib",
    }.items():
        directory.mkdir(parents=True, exist_ok=True)
        os.environ[variable] = str(directory)
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    notebook = nbformat.read(NOTEBOOK, as_version=4)
    nbformat.validate(notebook)
    code_cells = sum(cell.cell_type == "code" for cell in notebook.cells)
    print(f"Executing {code_cells} code cells in a fresh Python kernel...", flush=True)
    client = NotebookClient(
        notebook, timeout=300, kernel_name="python3", allow_errors=False,
        resources={"metadata": {"path": str(ROOT)}},
    )
    client.execute()
    nbformat.validate(notebook)
    errors = [
        output for cell in notebook.cells if cell.cell_type == "code"
        for output in cell.get("outputs", []) if output.output_type == "error"
    ]
    if errors:
        raise RuntimeError(f"Notebook has {len(errors)} error outputs.")
    if any(cell.execution_count is None for cell in notebook.cells if cell.cell_type == "code"):
        raise RuntimeError("A code cell was not executed.")
    nbformat.write(notebook, NOTEBOOK)
    print(f"Executed and saved {NOTEBOOK.name}. Results and figures regenerated.", flush=True)


if __name__ == "__main__":
    main()
