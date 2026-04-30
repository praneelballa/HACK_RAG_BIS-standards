import re
import fitz
import json
import os

CATEGORIES_MAP = {
    "SECTION 1": "CEMENT AND CONCRETE",
    "SECTION 2": "BUILDING LIMES",
    "SECTION 3": "STONES",
    "SECTION 4": "WOOD PRODUCTS FOR BUILDING",
    "SECTION 5": "GYPSUM BUILDING MATERIALS",
    "SECTION 6": "TIMBER",
    "SECTION 7": "BITUMEN AND TAR PRODUCTS",
    "SECTION 8": "FLOOR, WALL, ROOF COVERINGS AND FINISHES",
    "SECTION 9": "WATER PROOFING AND DAMP PROOFING MATERIALS",
    "SECTION 10": "SANITARY APPLIANCES AND WATER FITTINGS",
    "SECTION 11": "BUILDER'S HARDWARE",
    "SECTION 12": "WOOD PRODUCTS",
    "SECTION 13": "DOORS, WINDOWS AND SHUTTERS",
    "SECTION 14": "CONCRETE REINFORCEMENT",
    "SECTION 15": "STRUCTURAL STEELS",
    "SECTION 16": "LIGHT METAL AND THEIR ALLOYS",
    "SECTION 17": "STRUCTURAL SHAPES",
    "SECTION 18": "WELDING ELECTRODES AND WIRES",
    "SECTION 19": "THREADED FASTENERS AND RIVETS",
    "SECTION 20": "WIRE ROPES AND WIRE PRODUCTS",
    "SECTION 21": "GLASS",
    "SECTION 22": "FILLERS, STOPPERS AND PUTTIES",
    "SECTION 23": "THERMAL INSULATION MATERIALS",
    "SECTION 24": "PLASTICS",
    "SECTION 25": "CONDUCTORS AND CABLES",
    "SECTION 26": "WIRING ACCESSORIES",
    "SECTION 27": "GENERAL"
}

# ✅ Updated regex — captures (Part N) and (Section N) variants
IS_HEADER_RE = re.compile(
    r"^\s*IS\s+(?P<number>\d+)"
    r"(?:\s*\(Part\s*(?P<part>\d+)\))?"
    r"(?:\s*\(Section\s*(?P<section>\d+)\))?"
    r"\s*:\s*(?P<year>\d{4})",
    re.MULTILINE | re.IGNORECASE
)

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_scope(text):
    scope_match = re.search(
        r"1\.\s*Scope\s*—?\s*(.*?)(?=\n\s*2\.\s|(?:\n\s*IS\s+\d+)|$)",
        text, re.DOTALL | re.IGNORECASE
    )
    if scope_match:
        return clean_text(scope_match.group(1))
    return clean_text(text[:600])

def build_is_id(number, part, section, year):
    """Build a normalized IS identifier like 'IS 2185 (Part 2): 1983'"""
    result = f"IS {number}"
    if part:
        result += f" (Part {part})"
    if section:
        result += f" (Section {section})"
    result += f": {year}"
    return result

def parse_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Cannot find {pdf_path}")

    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"

    matches = list(IS_HEADER_RE.finditer(full_text))
    current_category = "GENERAL"
    all_standards = []

    for i, m in enumerate(matches):
        start_pos = m.start()
        end_pos = matches[i+1].start() if i+1 < len(matches) else len(full_text)

        block = full_text[start_pos:end_pos]

        # Update category by looking back
        lookback_window = full_text[max(0, start_pos-2000):start_pos]
        for sec_id, sec_name in CATEGORIES_MAP.items():
            if sec_id in lookback_window:
                current_category = sec_name

        # Extract components
        number  = m.group("number")
        part    = m.group("part")
        section = m.group("section")
        year    = m.group("year")

        # ✅ Build full IS identifier with part/section
        full_is_id = build_is_id(number, part, section, year)

        # Extract title
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        title = lines[0] if lines else "Unknown Title"
        title = re.sub(
            r"IS\s+\d+(\s*\(Part\s*\d+\))?(\s*\(Section\s*\d+\))?\s*:\s*\d{4}",
            "", title, flags=re.I
        ).strip(" ,-—")

        all_standards.append({
            "is_number": number,
            "part": part,
            "section": section,
            "year": year,
            "full_is_id": full_is_id,      # ✅ e.g. "IS 2185 (Part 2): 1983"
            "category": current_category,
            "title": title,
            "scope": extract_scope(block),
        })

    return all_standards

if __name__ == "__main__":
    pdf_file = "dataset.pdf"
    try:
        data = parse_pdf(pdf_file)
        with open("raw_standards.json", "w") as f:
            json.dump(data, f, indent=4)
        print(f"✅ Success! Extracted {len(data)} standards into raw_standards.json")
        
        # Show part-number standards found
        parts = [d for d in data if d.get('part')]
        print(f"📦 Found {len(parts)} standards with Part numbers")
        for p in parts[:5]:
            print(f"   → {p['full_is_id']}: {p['title'][:60]}")
    except Exception as e:
        print(f"❌ Error: {e}")