import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("models/gemini-2.0-flash-exp")

def ask_gemini(prompt: str):
    response = model.generate_content([prompt])
    return response.text.strip()

def handle_update(command: str):
    section_map = {
        "project": "../front-end/app/projects/page.tsx",
        "experience": "../front-end/app/experience/page.tsx",
        "honor": "../front-end/app/honors/page.tsx",
        "post": "../front-end/app/posts/page.tsx"
    }

    section = next((key for key in section_map if key in command.lower()), None)
    if not section:
        return "❌ Could not determine which section to update."

    file_path = section_map[section]

    # Prompt to Gemini: full object format with dummy id
    prompt = f"""
You're a TypeScript + React developer.

Based on this instruction:
"{command}"

Generate a single valid JavaScript object for a Next.js project array like this:

{{
  id: 999,
  title: "Project Title",
  description: "A one-line summary of the project.",
  features: ["Feature 1", "Feature 2", "Feature 3"],
  technologies: ["Tech 1", "Tech 2", "Tech 3"],
  imageUrl: "/projects/placeholder.jpg",
  demoUrl: "#",
  githubUrl: "#"
}}

⚠️ Instructions:
- Only return the object (no array, no explanation, no backticks).
- Use id: 999 — we will replace it automatically.
"""

    jsx_object = ask_gemini(prompt)

    try:
        with open(file_path, "r") as f:
            lines = f.readlines()

        # Extract all current id values
        current_ids = []
        for line in lines:
            if "id:" in line:
                try:
                    id_value = int(line.split("id:")[1].split(",")[0].strip())
                    current_ids.append(id_value)
                except:
                    pass

        new_id = max(current_ids, default=0) + 1
        jsx_object = jsx_object.replace("id: 999", f"id: {new_id}")

        # Insert object immediately after array starts
        insert_idx = next(
            i for i, line in enumerate(lines) if "const" in line and "[" in line
        ) + 1

        lines.insert(insert_idx, "  " + jsx_object + ",\n")

        with open(file_path, "w") as f:
            f.writelines(lines)

        return f"✅ {section.capitalize()} updated with new project ID {new_id}!"
    except Exception as e:
        return f"❌ File update failed: {str(e)}"
