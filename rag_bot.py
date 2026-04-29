import base64
import json
import os
from typing import Any, Dict, List, TypedDict

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langgraph.graph import END, StateGraph
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.readers.file import PDFReader
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is missing in .env")

client = OpenAI(api_key=api_key)

CATALOG_RULES_PATH = "extracted_data/catalog_rules.json"
TRANSCRIPT_RECORD_PATH = "extracted_data/transcript_record.json"
UPLOADS_DIR = "uploads"


class ChatState(TypedDict):
    question: str
    route: str
    retrieved_chunks: List[str]
    citations: List[str]
    catalog_rules: Dict[str, Any]
    transcript_record: Dict[str, Any]
    calc_result: Dict[str, Any]
    answer: str


def ensure_dirs() -> None:
    os.makedirs("extracted_data", exist_ok=True)
    os.makedirs("processed_data", exist_ok=True)
    os.makedirs(UPLOADS_DIR, exist_ok=True)


def save_json(path: str, data: Dict[str, Any]) -> None:
    ensure_dirs()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def clean_webpage_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text("\n")
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def fetch_catalog_text(url: str) -> str:
    resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    return clean_webpage_text(resp.text)


def extract_catalog_rules_from_text(catalog_text: str, source_url: str) -> Dict[str, Any]:
    schema = {
        "type": "object",
        "properties": {
            "program_name": {"type": "string"},
            "required_credits": {"type": ["number", "null"]},
            "minimum_cgpa_for_graduation": {"type": ["number", "null"]},
            "tracks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "track_name": {"type": "string"},
                        "required_credits": {"type": ["number", "null"]},
                        "notes": {"type": "string"},
                    },
                    "required": ["track_name", "required_credits", "notes"],
                    "additionalProperties": False,
                },
            },
            "required_courses": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "course_name": {"type": "string"},
                        "credits": {"type": ["number", "null"]},
                        "category": {"type": "string"},
                    },
                    "required": ["course_name", "credits", "category"],
                    "additionalProperties": False,
                },
            },
            "elective_credit_requirement": {"type": ["number", "null"]},
            "exceptions_and_notes": {
                "type": "array",
                "items": {"type": "string"},
            },
            "source_url": {"type": "string"},
        },
        "required": [
            "program_name",
            "required_credits",
            "minimum_cgpa_for_graduation",
            "tracks",
            "required_courses",
            "elective_credit_requirement",
            "exceptions_and_notes",
            "source_url",
        ],
        "additionalProperties": False,
    }

    prompt = f"""
Extract structured academic program rules from the catalog text below.

Return only factual data present in the text.
If a field is not clearly present, return null for numeric fields and [] for arrays.
Do not invent missing courses or policies.

Catalog source URL:
{source_url}

Catalog text:
{catalog_text[:40000]}
"""

    resp = client.responses.create(
        model="gpt-4.1",
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "catalog_rules",
                "schema": schema,
                "strict": True,
            }
        },
    )

    return json.loads(resp.output_text)


def parse_transcript_text_to_record(transcript_text: str) -> Dict[str, Any]:
    schema = {
        "type": "object",
        "properties": {
            "student_name": {"type": ["string", "null"]},
            "program": {"type": ["string", "null"]},
            "completed_courses": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "course": {"type": "string"},
                        "credits": {"type": "number"},
                        "grade": {"type": "string"},
                    },
                    "required": ["course", "credits", "grade"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["student_name", "program", "completed_courses"],
        "additionalProperties": False,
    }

    prompt = f"""
Extract a structured student record from the transcript text below.

Rules:
- Only include completed courses that clearly have a grade and credits.
- Preserve actual credit values, including 1-credit or 2-credit courses.
- Do not assume standard credits.
- Ignore rows that are not clearly completed courses.

Transcript text:
{transcript_text[:40000]}
"""

    resp = client.responses.create(
        model="gpt-4.1",
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "transcript_record",
                "schema": schema,
                "strict": True,
            }
        },
    )

    return json.loads(resp.output_text)


def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    ensure_dirs()
    temp_path = os.path.join(UPLOADS_DIR, "temp_transcript.pdf")

    with open(temp_path, "wb") as f:
        f.write(file_bytes)

    docs = SimpleDirectoryReader(
        input_files=[temp_path],
        file_extractor={".pdf": PDFReader()},
    ).load_data()

    text_parts = []
    for doc in docs:
        text_parts.append(getattr(doc, "text", ""))

    return "\n".join(text_parts).strip()


def parse_transcript_image(file_bytes: bytes, content_type: str) -> Dict[str, Any]:
    schema = {
        "type": "object",
        "properties": {
            "student_name": {"type": ["string", "null"]},
            "program": {"type": ["string", "null"]},
            "completed_courses": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "course": {"type": "string"},
                        "credits": {"type": "number"},
                        "grade": {"type": "string"},
                    },
                    "required": ["course", "credits", "grade"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["student_name", "program", "completed_courses"],
        "additionalProperties": False,
    }

    base64_data = base64.b64encode(file_bytes).decode("utf-8")
    data_url = f"data:{content_type};base64,{base64_data}"

    resp = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Extract a structured student record from this transcript image. "
                            "Only include courses with clearly visible course name, credits, and final grade. "
                            "Preserve actual credit values exactly."
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": data_url,
                    },
                ],
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "transcript_record_from_image",
                "schema": schema,
                "strict": True,
            }
        },
    )

    return json.loads(resp.output_text)


def ingest_catalog_url(url: str) -> Dict[str, Any]:
    catalog_text = fetch_catalog_text(url)
    rules = extract_catalog_rules_from_text(catalog_text, url)
    save_json(CATALOG_RULES_PATH, rules)
    return {
        "status": "success",
        "message": "Catalog URL ingested successfully.",
        "catalog_rules": rules,
    }


def ingest_transcript_text(transcript_text: str) -> Dict[str, Any]:
    record = parse_transcript_text_to_record(transcript_text)
    save_json(TRANSCRIPT_RECORD_PATH, record)
    return {
        "status": "success",
        "message": "Transcript text parsed successfully.",
        "transcript_record": record,
    }


def ingest_transcript_file(file_bytes: bytes, filename: str, content_type: str) -> Dict[str, Any]:
    filename_lower = filename.lower()

    if filename_lower.endswith(".pdf") or content_type == "application/pdf":
        extracted_text = extract_text_from_pdf_bytes(file_bytes)
        record = parse_transcript_text_to_record(extracted_text)

    elif content_type.startswith("image/") or filename_lower.endswith(
        (".png", ".jpg", ".jpeg", ".webp")
    ):
        record = parse_transcript_image(file_bytes, content_type)

    elif filename_lower.endswith(".txt") or content_type.startswith("text/"):
        record = parse_transcript_text_to_record(
            file_bytes.decode("utf-8", errors="ignore")
        )

    else:
        return {
            "status": "error",
            "message": f"Unsupported file type: {filename} ({content_type})",
        }

    save_json(TRANSCRIPT_RECORD_PATH, record)
    return {
        "status": "success",
        "message": "Transcript file ingested successfully.",
        "transcript_record": record,
    }


def build_index():
    docs = SimpleDirectoryReader(
        input_dir="processed_data",
        recursive=True,
        required_exts=[".pdf", ".txt", ".md"],
        file_extractor={".pdf": PDFReader()},
    ).load_data()

    if not docs:
        raise ValueError("No documents found in processed_data/")

    return VectorStoreIndex.from_documents(docs).as_query_engine(similarity_top_k=4)


query_engine = build_index()


def load_context(state: ChatState) -> ChatState:
    return {
        **state,
        "catalog_rules": load_json(CATALOG_RULES_PATH),
        "transcript_record": load_json(TRANSCRIPT_RECORD_PATH),
    }


def classify_intent(state: ChatState) -> ChatState:
    q = state["question"].lower()

    calc_words = [
        "cgpa",
        "gpa",
        "credit",
        "credits",
        "remaining",
        "left",
        "how many more",
        "graduate",
        "eligible",
    ]
    reasoning_words = [
        "should i",
        "which",
        "recommend",
        "difference",
        "compare",
        "why",
        "advise",
    ]

    has_calc = any(w in q for w in calc_words)
    has_reason = any(w in q for w in reasoning_words)

    if has_calc and has_reason:
        route = "hybrid"
    elif has_calc:
        route = "calculation"
    elif has_reason:
        route = "reasoning"
    else:
        route = "retrieval"

    return {**state, "route": route}


def retrieve_docs(state: ChatState) -> ChatState:
    if state["route"] == "calculation":
        return {**state, "retrieved_chunks": [], "citations": []}

    response = query_engine.query(state["question"])
    source_nodes = getattr(response, "source_nodes", []) or []

    chunks: List[str] = []
    citations: List[str] = []
    seen = set()

    for i, node in enumerate(source_nodes, start=1):
        text = node.node.get_content().strip()
        if not text:
            continue

        meta = node.node.metadata or {}
        file_name = (
            meta.get("file_name")
            or meta.get("filename")
            or meta.get("source")
            or f"Source {i}"
        )

        chunks.append(text[:1200])

        if file_name not in seen:
            seen.add(file_name)
            citations.append(file_name)

    return {
        **state,
        "retrieved_chunks": chunks,
        "citations": citations,
    }


def get_grade_points_map() -> Dict[str, float]:
    return {
        "A": 4.0,
        "A-": 3.7,
        "B+": 3.3,
        "B": 3.0,
        "B-": 2.7,
        "C+": 2.3,
        "C": 2.0,
        "C-": 1.7,
        "D+": 1.3,
        "D": 1.0,
        "F": 0.0,
    }


def calculate_cgpa(completed_courses: List[Dict[str, Any]]) -> Dict[str, Any]:
    grade_points = get_grade_points_map()
    total_quality_points = 0.0
    total_credits = 0.0
    breakdown = []

    for item in completed_courses:
        course = item["course"]
        credits = float(item["credits"])
        grade = item["grade"].strip().upper()

        if grade not in grade_points:
            continue

        points = grade_points[grade]
        quality_points = credits * points

        total_credits += credits
        total_quality_points += quality_points

        breakdown.append(
            {
                "course": course,
                "credits": credits,
                "grade": grade,
                "grade_points": points,
                "quality_points": round(quality_points, 3),
            }
        )

    cgpa = total_quality_points / total_credits if total_credits > 0 else 0.0

    return {
        "type": "cgpa",
        "total_credits": round(total_credits, 3),
        "total_quality_points": round(total_quality_points, 3),
        "cgpa": round(cgpa, 3),
        "breakdown": breakdown,
    }


def calculate_remaining_credits(
    transcript_record: Dict[str, Any],
    catalog_rules: Dict[str, Any],
) -> Dict[str, Any]:
    completed_courses = transcript_record.get("completed_courses", [])
    completed_credits = sum(float(c.get("credits", 0)) for c in completed_courses)

    required_credits = catalog_rules.get("required_credits")
    if required_credits is None:
        return {
            "type": "error",
            "message": "I could not find the required total credits from the catalog data.",
        }

    remaining = max(float(required_credits) - completed_credits, 0.0)

    return {
        "type": "remaining_credits",
        "completed_credits": round(completed_credits, 3),
        "required_credits": round(float(required_credits), 3),
        "remaining_credits": round(remaining, 3),
    }


def calculate_graduation_status(
    transcript_record: Dict[str, Any],
    catalog_rules: Dict[str, Any],
) -> Dict[str, Any]:
    gpa_result = calculate_cgpa(transcript_record.get("completed_courses", []))
    remaining_result = calculate_remaining_credits(transcript_record, catalog_rules)

    min_cgpa = catalog_rules.get("minimum_cgpa_for_graduation")
    if min_cgpa is None:
        min_cgpa = 0.0

    if remaining_result.get("type") == "error":
        return remaining_result

    eligible = (
        remaining_result["remaining_credits"] <= 0
        and gpa_result["cgpa"] >= float(min_cgpa)
    )

    return {
        "type": "graduation_status",
        "cgpa": gpa_result["cgpa"],
        "minimum_cgpa_for_graduation": float(min_cgpa),
        "completed_credits": remaining_result["completed_credits"],
        "required_credits": remaining_result["required_credits"],
        "remaining_credits": remaining_result["remaining_credits"],
        "eligible": eligible,
    }


def calculate_tools(state: ChatState) -> ChatState:
    q = state["question"].lower()
    record = state["transcript_record"]
    rules = state["catalog_rules"]

    calc_result: Dict[str, Any] = {}

    if "my cgpa" in q or "my gpa" in q:
        calc_result = calculate_cgpa(record.get("completed_courses", []))

    elif "remaining credits" in q or "credits left" in q or "how many more credits" in q:
        calc_result = calculate_remaining_credits(record, rules)

    elif "can i graduate" in q or "am i eligible to graduate" in q:
        calc_result = calculate_graduation_status(record, rules)

    return {**state, "calc_result": calc_result}


def build_answer_prompt(state: ChatState) -> str:
    evidence = "\n\n".join(
        f"[{i + 1}] {chunk}" for i, chunk in enumerate(state["retrieved_chunks"])
    )

    return f"""
You are a smart academic assistant.

Use:
- retrieved evidence for factual statements
- transcript data for completed courses
- catalog rules for requirements
- tool results for calculations

Question:
{state["question"]}

Retrieved Evidence:
{evidence if evidence else "No retrieved evidence."}

Catalog Rules:
{json.dumps(state["catalog_rules"], indent=2)}

Transcript Record:
{json.dumps(state["transcript_record"], indent=2)}

Calculation Result:
{json.dumps(state["calc_result"], indent=2)}

Instructions:
- If the question is about credits, CGPA, or graduation, trust the tool result.
- If the catalog has exceptions or caveats, mention them.
- Use inline citations like [1], [2] when relying on retrieved evidence.
- Do not invent missing values.
- Be clear when more information is needed.
"""


def answer(state: ChatState) -> ChatState:
    if (
        state["route"] in ["retrieval", "reasoning"]
        and not state["retrieved_chunks"]
        and not state["calc_result"]
    ):
        return {
            **state,
            "answer": "I don't know based on the available sources.",
        }

    if state["calc_result"].get("type") == "error":
        return {
            **state,
            "answer": state["calc_result"]["message"],
        }

    prompt = build_answer_prompt(state)

    resp = client.responses.create(
        model="gpt-4.1",
        input=prompt,
    )

    final_text = resp.output_text.strip()

    if state["citations"]:
        final_text += "\n\nSources:\n" + "\n".join(
            f"[{i + 1}] {name}" for i, name in enumerate(state["citations"])
        )

    return {**state, "answer": final_text}


graph = StateGraph(ChatState)
graph.add_node("load_context", load_context)
graph.add_node("classify", classify_intent)
graph.add_node("retrieve", retrieve_docs)
graph.add_node("calculate", calculate_tools)
graph.add_node("answer", answer)

graph.set_entry_point("load_context")
graph.add_edge("load_context", "classify")
graph.add_edge("classify", "retrieve")
graph.add_edge("retrieve", "calculate")
graph.add_edge("calculate", "answer")
graph.add_edge("answer", END)

app = graph.compile()
