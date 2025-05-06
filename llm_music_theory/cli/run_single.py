# cli/run_single.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import argparse
from llm_music_theory.core.dispatcher import get_llm
from models.base import PromptInput



def main():
    parser = argparse.ArgumentParser(description="Run a single LLM prompt")
    parser.add_argument("--model", required=True, help="Model name: chatgpt, gemini, claude, deepseek")
    parser.add_argument("--question", required=True, help="Question ID (e.g. Q4b)")
    parser.add_argument("--format", required=True, help="Encoding format (e.g. mei, abc, krn, musicxml)")
    parser.add_argument("--context", action="store_true", help="Use context version of question")

    args = parser.parse_args()

    # This is the key line: it gives you the correct model class
    llm = get_llm(args.model)

    # Example prompt
    prompt = PromptInput(
        system_prompt="You are a helpful assistant.",
        user_prompt="What is a cadence in music theory?",
        temperature=0.3
    )

    response = llm.query(prompt)
    print("Response:\n", response)


if __name__ == "__main__":
    main()
