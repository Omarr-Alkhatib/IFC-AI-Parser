import os
import sys
import argparse
import ifcopenshell
import ollama

def parse_arguments():
    parser = argparse.ArgumentParser(description="IFC BIM Parser & Local AI Construction Assistant")
    parser.add_argument("--file", type=str, default="Example.ifc", help="Path to the IFC building model file")
    parser.add_argument("--model", type=str, default="llama3.2", help="Ollama model name to use (e.g., llama3.2, mistral)")
    parser.add_argument("--output", type=str, default="building_report.md", help="Filename for the exported markdown report")
    return parser.parse_args()

def extract_ifc_data(file_path):
    print(f"[*] Opening and parsing IFC file: {file_path}...")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' not found. Please place a valid IFC file in this directory.")
    
    model = ifcopenshell.open(file_path)
    
    # 1. Project Metadata
    project = model.by_type("IfcProject")[0] if model.by_type("IfcProject") else None
    project_name = project.Name if project and project.Name else "Unnamed Project"
    
    # 2. Key Element Counts (Structural & Architectural Components)
    element_types = ["IfcWall", "IfcSlab", "IfcDoor", "IfcWindow", "IfcColumn", "IfcBeam", "IfcStair"]
    counts = {}
    for etype in element_types:
        counts[etype] = len(model.by_type(etype))
        
    # 3. Spatial Structure (Storeys / Levels)
    storeys = model.by_type("IfcBuildingStorey")
    storey_names = [s.Name for s in storeys if s.Name]
    
    # 4. Materials Extraction
    materials = model.by_type("IfcMaterial")
    material_names = [m.Name for m in materials if m.Name]
    
    # Compile structured text context for the AI agent
    report_lines = [
        f"# BIM Model Analysis Report: {project_name}",
        f"- **Source File:** `{file_path}`",
        f"- **Building Storeys / Levels ({len(storey_names)}):** {', '.join(storey_names) if storey_names else 'None specified'}",
        f"\n## 📊 Element Quantities Breakdown:",
    ]
    for etype, count in counts.items():
        report_lines.append(f"- **{etype.replace('Ifc', '')}:** {count} units")
        
    report_lines.append(f"\n## 🧱 Identified Materials ({len(material_names)}):")
    if material_names:
        for mat in material_names[:10]: # Limit list length for clarity
            report_lines.append(f"- {mat}")
    else:
        report_lines.append("- No explicit standalone IfcMaterial entities found.")

    # Include a few sample element IDs for traceability
    report_lines.append(f"\n## 🔍 Sample Element Identifiers:")
    for etype in ["IfcWall", "IfcColumn", "IfcBeam"]:
        elements = model.by_type(etype)
        if elements:
            report_lines.append(f"### {etype.replace('Ifc', '')}s (Sample):")
            for el in elements[:2]: # Grab first 2 elements as samples
                name = el.Name or "Unnamed"
                report_lines.append(f"  * **ID:** `{el.GlobalId}` | **Name:** {name}")

    return "\n".join(report_lines)

def generate_ai_report(building_context, model_name="llama3.2"):
    print(f"[*] Sending structured data to local Ollama agent (Model: {model_name})...")
    
    prompt = f"""
    You are an expert construction AI quantity surveyor and structural engineering assistant. 
    Analyze the following technical data extracted automatically from an IFC building model:

    {building_context}

    Task: Write a comprehensive, professional Executive Summary for a Project Manager or Chief Estimator. 
    Your response must include:
    1. A high-level assessment of the building's scale, complexity, and structural profile based on the elements and storeys.
    2. Key considerations or potential cost estimation and scheduling challenges.
    3. Three concrete, actionable recommendations for the pre-construction engineering team.
    """

    response = ollama.chat(
        model=model_name,
        messages=[{'role': 'user', 'content': prompt}]
    )
    
    return response['message']['content']

def main():
    args = parse_arguments()
    try:
        # Step 1: Extract structured data
        structured_data = extract_ifc_data(args.file)
        
        print("\n--- Extracted Data Preview ---")
        print(structured_data)
        
        # Step 2: Query local Ollama model
        ai_insights = generate_ai_report(structured_data, model_name=args.model)
        
        # Step 3: Combine data and AI summary into a final Markdown report
        final_report = f"{structured_data}\n\n---\n\n## 🤖 AI Executive Summary & Recommendations\n\n{ai_insights}\n"
        
        # Step 4: Save to file
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(final_report)
            
        print(f"[+] Success! Full analysis report saved successfully to: `{args.output}`")
        
    except Exception as e:
        print(f"[!] Error: {e}")
        print("[Tip] Ensure Ollama is running (`ollama serve`) and you have placed a sample IFC file (e.g., Example.ifc) in this folder.")

if __name__ == "__main__":
    main()