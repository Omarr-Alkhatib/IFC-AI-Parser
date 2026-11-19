# 🏗️ BIM & Local AI Quantity Surveying Assistant

A Python CLI and containerized automation tool that parses 3D Building Information Modeling (`.ifc`) files using `IfcOpenShell`, extracts structural and material metadata, and uses a **local AI agent via Ollama** to generate executive summaries and pre-construction notes without sending building data to external cloud APIs.

---

## 🎯 Why This Project
- **Open BIM Parsing:** Reads standard `.ifc` files directly via `IfcOpenShell` to count elements (walls, slabs, doors, windows, columns, beams, stairs), list building storeys, inspect materials, and pull sample IDs.
- **Local AI Privacy:** Uses a local Ollama model (such as `llama3.2`) so proprietary project data stays on your own machine.
- **CLI & Container Ready:** Runs directly from the command line or inside a Docker container.

---

## 📂 Project Structure

```text
.
├── app.py              # CLI entrypoint, IFC metadata extraction, and Ollama report generator
├── requirements.txt    # Python dependencies (ifcopenshell, ollama)
├── Dockerfile          # Container build definition (Python slim image)
├── .gitignore          # Ignores cache, virtual environments, outputs, and .ifc files
└── README.md           # Project documentation
```

---

## 🚀 Usage

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com/) with a locally available model
- Docker (for containerized execution)


### 1. CLI Usage

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py --file Example.ifc
```

**Available arguments:**

| Argument | Description | Default |
|---|---|---|
| `--file` | Path to the input IFC file | `Example.ifc` |
| `--model` | Ollama model to use | `llama3.2` |
| `--output` | Output Markdown report filename | `building_report.md` |

Example with custom arguments:

```bash
python app.py --file Duplex.ifc --model mistral --output duplex_analysis.md
```

The application parses the IFC file, extracts building metadata, passes the extracted information to the local Ollama model, and generates a Markdown report containing an executive summary and pre-construction recommendations.

### 2. Docker Usage

Build the Docker image:

```bash
docker build -t ifc-ai-parser .
```

Run the container:

**Linux:**

```bash
docker run --rm \
  -v "$(pwd):/data" \
  ifc-ai-parser \
  --file /data/Example.ifc \
  --model llama3.2 \
  --output /data/building_report.md
```

**Windows (PowerShell):**

```powershell
docker run --rm `
  -v "${PWD}:/data" `
  ifc-ai-parser `
  --file /data/Example.ifc `
  --model llama3.2 `
  --output /data/building_report.md
```

**Note:** Ollama runs separately from the application container. By default, it listens on `localhost`, which is not directly accessible from inside Docker. Ollama's host binding and the application's connection configuration must be adjusted to allow communication between the container and the host.
