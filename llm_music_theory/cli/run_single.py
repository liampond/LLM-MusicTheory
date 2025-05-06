import argparse
from pathlib import Path
from dotenv import load_dotenv
import os

from core.dispatcher import get_llm
from core.runner import PromptRunner

# --- Load environment variables ---
load_dotenv()

# --- CLI Argument Parser ---
parser = argparse.ArgumentParser(description="Run a single LLM music theory prompt.")
parser.add_argument("--question", required=True, help="Question number (e.g. Q1a)")
parser.add_argument("--datatype", required=True, choices=["mei", "musicxml", "abc", "humdrum"], help="Encoding format")
parser.add_argument("--context", action="store_true", help="Include context guides")
parser.add_argument("--examdate", default="August2024", help="Exam version or folder name")
parser.add_argument("--temperature", type=float, default=0.0, help="LLM temperature (default=0.0)")
parser.add_argument("--model", required=True, choices=["chatgpt", "claude", "gemini", "deepseek"], help="Which LLM to use")
args = parser.parse_args()

# --- Base Directories ---
base_path = Path(__file__).resolve().parent.parent
base_dirs = {
    "prompts": base_path / "prompts",
    "questions": base_path / "prompts" / "questions",
    "guides": base_path / "prompts" / "guides",
    "encoded": base_path / "encoded"
}

# --- Load model ---
model = get_llm(args.model)

# --- Initialize and run the prompt ---
runner = PromptRunner(
    model=model,
    question_number=args.question,
    datatype=args.datatype,
    context=args.context,
    exam_date=args.examdate,
    base_dirs=base_dirs,
    temperature=args.temperature
)

print(f"\n🧠 Running {args.question} [{args.datatype.upper()}] (context: {args.context})...")
response = runner.run()

# --- Output ---
print("\n📝 Model Response:\n")
print(response)
