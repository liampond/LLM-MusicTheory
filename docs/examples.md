# Examples

Practical examples of using LLM-MusicTheory for various music analysis tasks.

## Basic Usage Examples

### Example 1: Single Question Analysis

**Goal**: Analyze a counterpoint exercise with different models

```bash
# Using Gemini with MusicXML context
python -m llm_music_theory.cli.run_single \
  --question Q1b \
  --encoded_type musicxml \
  --model gemini-2.0-flash-exp \
  --context

# Using GPT-4 without context
python -m llm_music_theory.cli.run_single \
  --question Q1b \
  --model gpt-4o \
  --no-context

# Using Claude with MEI format
python -m llm_music_theory.cli.run_single \
  --question Q1b \
  --encoded_type mei \
  --model claude-3-5-sonnet-20241022 \
  --context
```

**Expected Output Structure**:
```
output/
├── context/
│   ├── gemini-2.0-flash-exp/
│   │   └── Q1b.musicxml
│   └── claude-3-5-sonnet-20241022/
│       └── Q1b.mei
└── no_context/
    └── gpt-4o/
        └── Q1b.txt
```

### Example 2: Format Comparison Study

**Goal**: Compare how models handle different music encoding formats

```bash
#!/bin/bash
# compare_formats.sh

question="Q1b"
model="gemini-2.0-flash-exp"
formats=("musicxml" "mei" "abc" "humdrum")

echo "Comparing formats for $question with $model"

for format in "${formats[@]}"; do
    echo "Processing $format format..."
    python -m llm_music_theory.cli.run_single \
        --question "$question" \
        --encoded_type "$format" \
        --model "$model" \
        --context
    
    echo "Completed $format"
    sleep 2  # Rate limiting
done

echo "Format comparison complete!"
echo "Results saved in output/context/$model/"
```

### Example 3: Model Comparison

**Goal**: Compare different models on the same question

```bash
#!/bin/bash
# compare_models.sh

question="Q1b"
encoded_type="musicxml"
models=("gemini-2.0-flash-exp" "gpt-4o" "claude-3-5-sonnet-20241022")

echo "Comparing models for $question with $encoded_type"

for model in "${models[@]}"; do
    echo "Testing $model..."
    python -m llm_music_theory.cli.run_single \
        --question "$question" \
        --encoded_type "$encoded_type" \
        --model "$model" \
        --context
    
    echo "Completed $model"
    sleep 5  # Rate limiting for API calls
done

echo "Model comparison complete!"
```

## Programmatic Usage Examples

### Example 4: Python Script for Systematic Analysis

```python
#!/usr/bin/env python3
"""
systematic_analysis.py - Comprehensive analysis script
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from llm_music_theory.core.runner import PromptRunner
from llm_music_theory.utils.logger import setup_logger

def main():
    """Run systematic music theory analysis."""
    
    # Setup
    logger = setup_logger("systematic_analysis", "INFO")
    runner = PromptRunner()
    
    # Define experimental conditions
    conditions = {
        "questions": ["Q1b"],
        "models": [
            "gemini-2.0-flash-exp",
            "gpt-4o",
            "claude-3-5-sonnet-20241022"
        ],
        "formats": ["musicxml", "mei", "abc", "humdrum"],
        "context_conditions": [True, False]
    }
    
    # Results storage
    results = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "conditions": conditions
        },
        "responses": {}
    }
    
    # Run analysis
    total_runs = (len(conditions["questions"]) * 
                  len(conditions["models"]) * 
                  len(conditions["formats"]) * 
                  len(conditions["context_conditions"]))
    
    logger.info(f"Starting systematic analysis: {total_runs} total runs")
    
    run_count = 0
    for question in conditions["questions"]:
        results["responses"][question] = {}
        
        for model in conditions["models"]:
            results["responses"][question][model] = {}
            
            for format_type in conditions["formats"]:
                results["responses"][question][model][format_type] = {}
                
                for use_context in conditions["context_conditions"]:
                    run_count += 1
                    context_str = "context" if use_context else "no_context"
                    
                    logger.info(f"Run {run_count}/{total_runs}: "
                              f"{question}, {model}, {format_type}, {context_str}")
                    
                    try:
                        if use_context:
                            response = runner.run_analysis(
                                question=question,
                                model_name=model,
                                encoded_type=format_type,
                                use_context=True
                            )
                        else:
                            response = runner.run_analysis(
                                question=question,
                                model_name=model,
                                use_context=False
                            )
                        
                        results["responses"][question][model][format_type][context_str] = {
                            "success": True,
                            "response": response,
                            "length": len(response)
                        }
                        
                        logger.info(f"Success: {len(response)} characters")
                        
                    except Exception as e:
                        error_msg = str(e)
                        results["responses"][question][model][format_type][context_str] = {
                            "success": False,
                            "error": error_msg
                        }
                        
                        logger.error(f"Failed: {error_msg}")
                    
                    # Rate limiting
                    await asyncio.sleep(2)
    
    # Save results
    output_file = Path("systematic_analysis_results.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Analysis complete! Results saved to {output_file}")
    
    # Print summary
    print_summary(results)

def print_summary(results):
    """Print analysis summary."""
    print("\n" + "="*50)
    print("ANALYSIS SUMMARY")
    print("="*50)
    
    total_runs = 0
    successful_runs = 0
    
    for question in results["responses"]:
        for model in results["responses"][question]:
            for format_type in results["responses"][question][model]:
                for context in results["responses"][question][model][format_type]:
                    total_runs += 1
                    if results["responses"][question][model][format_type][context].get("success"):
                        successful_runs += 1
    
    success_rate = (successful_runs / total_runs) * 100 if total_runs > 0 else 0
    
    print(f"Total runs: {total_runs}")
    print(f"Successful runs: {successful_runs}")
    print(f"Success rate: {success_rate:.1f}%")
    
    # Model-wise breakdown
    print("\nModel Performance:")
    for question in results["responses"]:
        for model in results["responses"][question]:
            model_success = 0
            model_total = 0
            
            for format_type in results["responses"][question][model]:
                for context in results["responses"][question][model][format_type]:
                    model_total += 1
                    if results["responses"][question][model][format_type][context].get("success"):
                        model_success += 1
            
            model_rate = (model_success / model_total) * 100 if model_total > 0 else 0
            print(f"  {model}: {model_success}/{model_total} ({model_rate:.1f}%)")

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 5: Research Data Collection

```python
#!/usr/bin/env python3
"""
research_collection.py - Academic research data collection
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from llm_music_theory.core.runner import PromptRunner
from llm_music_theory.utils.logger import setup_logger

class ResearchDataCollector:
    """Collect data for music theory research studies."""
    
    def __init__(self, study_name: str):
        self.study_name = study_name
        self.logger = setup_logger(f"research_{study_name}")
        self.runner = PromptRunner()
        self.results = []
        
        # Create output directory
        self.output_dir = Path(f"research_data/{study_name}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def collect_condition(self, condition_id: str, question: str, 
                         model: str, format_type: str, use_context: bool,
                         repetitions: int = 3):
        """Collect data for a single experimental condition."""
        
        self.logger.info(f"Collecting condition {condition_id}: "
                        f"{question}, {model}, {format_type}, "
                        f"context={use_context}, reps={repetitions}")
        
        for rep in range(repetitions):
            self.logger.info(f"  Repetition {rep + 1}/{repetitions}")
            
            try:
                start_time = datetime.now()
                
                if use_context:
                    response = self.runner.run_analysis(
                        question=question,
                        model_name=model,
                        encoded_type=format_type,
                        use_context=True
                    )
                else:
                    response = self.runner.run_analysis(
                        question=question,
                        model_name=model,
                        use_context=False
                    )
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                # Record result
                result = {
                    "condition_id": condition_id,
                    "repetition": rep + 1,
                    "timestamp": start_time.isoformat(),
                    "question": question,
                    "model": model,
                    "format_type": format_type if use_context else "none",
                    "use_context": use_context,
                    "response": response,
                    "response_length": len(response),
                    "duration_seconds": duration,
                    "success": True,
                    "error": None
                }
                
                self.results.append(result)
                
                # Save individual response
                filename = f"{condition_id}_rep{rep + 1}_{model}_{format_type if use_context else 'no_context'}.txt"
                response_file = self.output_dir / "responses" / filename
                response_file.parent.mkdir(exist_ok=True)
                
                with open(response_file, "w") as f:
                    f.write(response)
                
                self.logger.info(f"    Success: {len(response)} chars, {duration:.1f}s")
                
            except Exception as e:
                self.logger.error(f"    Failed: {e}")
                
                result = {
                    "condition_id": condition_id,
                    "repetition": rep + 1,
                    "timestamp": datetime.now().isoformat(),
                    "question": question,
                    "model": model,
                    "format_type": format_type if use_context else "none",
                    "use_context": use_context,
                    "response": None,
                    "response_length": 0,
                    "duration_seconds": 0,
                    "success": False,
                    "error": str(e)
                }
                
                self.results.append(result)
            
            # Rate limiting between repetitions
            import time
            time.sleep(3)
    
    def save_results(self):
        """Save collected results to files."""
        
        # Save as JSON
        json_file = self.output_dir / f"{self.study_name}_results.json"
        with open(json_file, "w") as f:
            json.dump({
                "study_name": self.study_name,
                "collection_date": datetime.now().isoformat(),
                "total_responses": len(self.results),
                "results": self.results
            }, f, indent=2)
        
        # Save as CSV for analysis
        csv_file = self.output_dir / f"{self.study_name}_results.csv"
        if self.results:
            fieldnames = self.results[0].keys()
            with open(csv_file, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.results)
        
        self.logger.info(f"Results saved: {json_file}, {csv_file}")
        return json_file, csv_file

def run_format_comparison_study():
    """Example: Format comparison study."""
    
    collector = ResearchDataCollector("format_comparison_2024")
    
    # Study design
    conditions = [
        {"id": "C1", "question": "Q1b", "model": "gemini-2.0-flash-exp", 
         "format": "musicxml", "context": True},
        {"id": "C2", "question": "Q1b", "model": "gemini-2.0-flash-exp", 
         "format": "mei", "context": True},
        {"id": "C3", "question": "Q1b", "model": "gemini-2.0-flash-exp", 
         "format": "abc", "context": True},
        {"id": "C4", "question": "Q1b", "model": "gemini-2.0-flash-exp", 
         "format": "humdrum", "context": True},
        {"id": "C5", "question": "Q1b", "model": "gemini-2.0-flash-exp", 
         "format": None, "context": False},
    ]
    
    # Collect data
    for condition in conditions:
        collector.collect_condition(
            condition_id=condition["id"],
            question=condition["question"],
            model=condition["model"],
            format_type=condition["format"],
            use_context=condition["context"],
            repetitions=5  # 5 repetitions per condition
        )
    
    # Save results
    json_file, csv_file = collector.save_results()
    print(f"Study complete! Results saved to {json_file}")

if __name__ == "__main__":
    run_format_comparison_study()
```

### Example 6: Custom Analysis Pipeline

```python
#!/usr/bin/env python3
"""
custom_pipeline.py - Custom analysis pipeline with preprocessing
"""

from llm_music_theory.core.runner import PromptRunner
from llm_music_theory.prompts.prompt_builder import PromptBuilder
from pathlib import Path
import re

class CustomAnalysisPipeline:
    """Custom pipeline for specialized music analysis."""
    
    def __init__(self):
        self.runner = PromptRunner()
        self.builder = PromptBuilder()
    
    def preprocess_response(self, response: str) -> dict:
        """Extract structured information from model response."""
        
        # Extract Roman numeral analysis
        roman_pattern = r'\b[IVXivx]+[^a-zA-Z]*\b'
        roman_numerals = re.findall(roman_pattern, response)
        
        # Extract chord names
        chord_pattern = r'\b[A-G][#b]?(?:maj|min|dim|aug|M|m|°|ø|\+)?[0-9]*\b'
        chord_names = re.findall(chord_pattern, response)
        
        # Extract key signatures
        key_pattern = r'\b[A-G][#b]?\s*(?:major|minor|maj|min)\b'
        keys = re.findall(key_pattern, response, re.IGNORECASE)
        
        # Count analysis depth
        technical_terms = [
            'cadence', 'modulation', 'sequence', 'suspension',
            'passing tone', 'neighbor tone', 'resolution',
            'voice leading', 'counterpoint'
        ]
        
        term_counts = {}
        for term in technical_terms:
            count = len(re.findall(term, response, re.IGNORECASE))
            term_counts[term] = count
        
        return {
            "raw_response": response,
            "roman_numerals": roman_numerals,
            "chord_names": chord_names,
            "keys": keys,
            "technical_term_usage": term_counts,
            "response_length": len(response),
            "analysis_depth_score": sum(term_counts.values())
        }
    
    def analyze_question_comprehensive(self, question: str, models: list, 
                                     formats: list) -> dict:
        """Run comprehensive analysis across models and formats."""
        
        results = {
            "question": question,
            "models": {},
            "comparative_analysis": {}
        }
        
        # Collect responses
        for model in models:
            results["models"][model] = {}
            
            # Context analysis for each format
            for format_type in formats:
                try:
                    response = self.runner.run_analysis(
                        question=question,
                        model_name=model,
                        encoded_type=format_type,
                        use_context=True
                    )
                    
                    processed = self.preprocess_response(response)
                    results["models"][model][format_type] = processed
                    
                except Exception as e:
                    results["models"][model][format_type] = {
                        "error": str(e)
                    }
            
            # No-context analysis
            try:
                response = self.runner.run_analysis(
                    question=question,
                    model_name=model,
                    use_context=False
                )
                
                processed = self.preprocess_response(response)
                results["models"][model]["no_context"] = processed
                
            except Exception as e:
                results["models"][model]["no_context"] = {
                    "error": str(e)
                }
        
        # Comparative analysis
        results["comparative_analysis"] = self.compare_analyses(results["models"])
        
        return results
    
    def compare_analyses(self, model_results: dict) -> dict:
        """Compare analyses across models and formats."""
        
        comparison = {
            "response_lengths": {},
            "analysis_depth": {},
            "technical_term_usage": {},
            "consistency_scores": {}
        }
        
        # Response length comparison
        for model in model_results:
            comparison["response_lengths"][model] = {}
            comparison["analysis_depth"][model] = {}
            
            for condition in model_results[model]:
                if "error" not in model_results[model][condition]:
                    length = model_results[model][condition]["response_length"]
                    depth = model_results[model][condition]["analysis_depth_score"]
                    
                    comparison["response_lengths"][model][condition] = length
                    comparison["analysis_depth"][model][condition] = depth
        
        # Technical term usage across models
        all_terms = set()
        for model in model_results:
            for condition in model_results[model]:
                if "technical_term_usage" in model_results[model][condition]:
                    terms = model_results[model][condition]["technical_term_usage"]
                    all_terms.update(terms.keys())
        
        for term in all_terms:
            comparison["technical_term_usage"][term] = {}
            for model in model_results:
                comparison["technical_term_usage"][term][model] = {}
                for condition in model_results[model]:
                    if "technical_term_usage" in model_results[model][condition]:
                        usage = model_results[model][condition]["technical_term_usage"]
                        comparison["technical_term_usage"][term][model][condition] = usage.get(term, 0)
        
        return comparison
    
    def save_comprehensive_results(self, results: dict, output_file: str):
        """Save comprehensive analysis results."""
        
        import json
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        
        # Also save a summary report
        summary_path = output_path.with_suffix('.summary.txt')
        self.generate_summary_report(results, summary_path)
        
        return output_path, summary_path
    
    def generate_summary_report(self, results: dict, output_path: Path):
        """Generate human-readable summary report."""
        
        with open(output_path, "w") as f:
            f.write(f"Analysis Summary for {results['question']}\n")
            f.write("=" * 50 + "\n\n")
            
            # Model performance overview
            f.write("Model Performance Overview:\n")
            f.write("-" * 30 + "\n")
            
            for model in results["models"]:
                f.write(f"\n{model}:\n")
                for condition in results["models"][model]:
                    if "error" in results["models"][model][condition]:
                        f.write(f"  {condition}: ERROR - {results['models'][model][condition]['error']}\n")
                    else:
                        length = results["models"][model][condition]["response_length"]
                        depth = results["models"][model][condition]["analysis_depth_score"]
                        f.write(f"  {condition}: {length} chars, depth score: {depth}\n")
            
            # Comparative analysis
            f.write("\n\nComparative Analysis:\n")
            f.write("-" * 30 + "\n")
            
            comparison = results["comparative_analysis"]
            
            # Average response lengths
            f.write("\nAverage Response Lengths:\n")
            for model in comparison["response_lengths"]:
                lengths = list(comparison["response_lengths"][model].values())
                if lengths:
                    avg_length = sum(lengths) / len(lengths)
                    f.write(f"  {model}: {avg_length:.0f} characters\n")
            
            # Analysis depth scores
            f.write("\nAnalysis Depth Scores:\n")
            for model in comparison["analysis_depth"]:
                depths = list(comparison["analysis_depth"][model].values())
                if depths:
                    avg_depth = sum(depths) / len(depths)
                    f.write(f"  {model}: {avg_depth:.1f} average depth\n")

def run_comprehensive_analysis():
    """Example: Run comprehensive analysis pipeline."""
    
    pipeline = CustomAnalysisPipeline()
    
    # Define analysis parameters
    question = "Q1b"
    models = ["gemini-2.0-flash-exp", "gpt-4o", "claude-3-5-sonnet-20241022"]
    formats = ["musicxml", "mei", "abc"]
    
    print(f"Running comprehensive analysis for {question}...")
    print(f"Models: {models}")
    print(f"Formats: {formats}")
    
    # Run analysis
    results = pipeline.analyze_question_comprehensive(question, models, formats)
    
    # Save results
    output_file = f"comprehensive_analysis_{question}.json"
    json_path, summary_path = pipeline.save_comprehensive_results(results, output_file)
    
    print(f"\nAnalysis complete!")
    print(f"Detailed results: {json_path}")
    print(f"Summary report: {summary_path}")

if __name__ == "__main__":
    run_comprehensive_analysis()
```

## Workflow Examples

### Example 7: Educational Assessment Workflow

```bash
#!/bin/bash
# educational_assessment.sh
# Workflow for educators testing student understanding

echo "Educational Assessment Workflow"
echo "==============================="

# Questions for different skill levels
beginner_questions=("Q1b")  # Add more beginner questions
intermediate_questions=()   # Add intermediate questions  
advanced_questions=()       # Add advanced questions

# Models optimized for education
educational_models=("gpt-4o-mini" "gemini-2.0-flash-exp" "claude-3-5-haiku-20241022")

# Test beginner level
echo "Testing beginner level questions..."
for question in "${beginner_questions[@]}"; do
    for model in "${educational_models[@]}"; do
        echo "  Processing $question with $model (with context)"
        python -m llm_music_theory.cli.run_single \
            --question "$question" \
            --encoded_type musicxml \
            --model "$model" \
            --context
        
        echo "  Processing $question with $model (without context)"
        python -m llm_music_theory.cli.run_single \
            --question "$question" \
            --model "$model" \
            --no-context
        
        sleep 2
    done
done

echo "Educational assessment complete!"
echo "Review results in output/ directory"
```

### Example 8: Research Publication Workflow

```python
#!/usr/bin/env python3
"""
publication_workflow.py - Generate data for academic publication
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from llm_music_theory.core.runner import PromptRunner

def generate_publication_dataset():
    """Generate dataset suitable for academic publication."""
    
    # Research parameters
    study_config = {
        "title": "LLM Music Theory Analysis Capabilities",
        "questions": ["Q1b"],  # Expand with your question set
        "models": {
            "gemini-2.0-flash-exp": "Google Gemini 2.0 Flash",
            "gpt-4o": "OpenAI GPT-4 Omni", 
            "claude-3-5-sonnet-20241022": "Anthropic Claude 3.5 Sonnet"
        },
        "formats": {
            "musicxml": "MusicXML",
            "mei": "Music Encoding Initiative",
            "abc": "ABC Notation", 
            "humdrum": "Humdrum"
        },
        "repetitions": 5
    }
    
    runner = PromptRunner()
    dataset = []
    
    print("Generating publication dataset...")
    print(f"Configuration: {json.dumps(study_config, indent=2)}")
    
    total_runs = (len(study_config["questions"]) * 
                  len(study_config["models"]) * 
                  (len(study_config["formats"]) + 1) *  # +1 for no-context
                  study_config["repetitions"])
    
    run_id = 0
    
    for question in study_config["questions"]:
        for model_id, model_name in study_config["models"].items():
            
            # Context conditions
            for format_id, format_name in study_config["formats"].items():
                for rep in range(study_config["repetitions"]):
                    run_id += 1
                    print(f"Run {run_id}/{total_runs}: {question}, {model_id}, {format_id}, rep {rep+1}")
                    
                    try:
                        start_time = datetime.now()
                        response = runner.run_analysis(
                            question=question,
                            model_name=model_id,
                            encoded_type=format_id,
                            use_context=True
                        )
                        end_time = datetime.now()
                        
                        dataset.append({
                            "run_id": run_id,
                            "question_id": question,
                            "model_id": model_id,
                            "model_name": model_name,
                            "format_id": format_id,
                            "format_name": format_name,
                            "context_condition": "with_context",
                            "repetition": rep + 1,
                            "timestamp": start_time.isoformat(),
                            "response": response,
                            "response_length": len(response),
                            "processing_time_seconds": (end_time - start_time).total_seconds(),
                            "success": True,
                            "error": None
                        })
                        
                    except Exception as e:
                        dataset.append({
                            "run_id": run_id,
                            "question_id": question,
                            "model_id": model_id,
                            "model_name": model_name,
                            "format_id": format_id,
                            "format_name": format_name,
                            "context_condition": "with_context",
                            "repetition": rep + 1,
                            "timestamp": datetime.now().isoformat(),
                            "response": None,
                            "response_length": 0,
                            "processing_time_seconds": 0,
                            "success": False,
                            "error": str(e)
                        })
                    
                    # Rate limiting
                    import time
                    time.sleep(3)
            
            # No context condition
            for rep in range(study_config["repetitions"]):
                run_id += 1
                print(f"Run {run_id}/{total_runs}: {question}, {model_id}, no_context, rep {rep+1}")
                
                try:
                    start_time = datetime.now()
                    response = runner.run_analysis(
                        question=question,
                        model_name=model_id,
                        use_context=False
                    )
                    end_time = datetime.now()
                    
                    dataset.append({
                        "run_id": run_id,
                        "question_id": question,
                        "model_id": model_id,
                        "model_name": model_name,
                        "format_id": None,
                        "format_name": None,
                        "context_condition": "no_context",
                        "repetition": rep + 1,
                        "timestamp": start_time.isoformat(),
                        "response": response,
                        "response_length": len(response),
                        "processing_time_seconds": (end_time - start_time).total_seconds(),
                        "success": True,
                        "error": None
                    })
                    
                except Exception as e:
                    dataset.append({
                        "run_id": run_id,
                        "question_id": question,
                        "model_id": model_id,
                        "model_name": model_name,
                        "format_id": None,
                        "format_name": None,
                        "context_condition": "no_context",
                        "repetition": rep + 1,
                        "timestamp": datetime.now().isoformat(),
                        "response": None,
                        "response_length": 0,
                        "processing_time_seconds": 0,
                        "success": False,
                        "error": str(e)
                    })
                
                # Rate limiting
                import time
                time.sleep(3)
    
    # Save dataset
    output_dir = Path("publication_data")
    output_dir.mkdir(exist_ok=True)
    
    # Save as CSV for statistical analysis
    csv_file = output_dir / "llm_music_theory_dataset.csv"
    with open(csv_file, "w", newline="") as f:
        if dataset:
            writer = csv.DictWriter(f, fieldnames=dataset[0].keys())
            writer.writeheader()
            writer.writerows(dataset)
    
    # Save as JSON for detailed analysis
    json_file = output_dir / "llm_music_theory_dataset.json"
    with open(json_file, "w") as f:
        json.dump({
            "study_configuration": study_config,
            "generation_timestamp": datetime.now().isoformat(),
            "total_runs": len(dataset),
            "successful_runs": sum(1 for d in dataset if d["success"]),
            "dataset": dataset
        }, f, indent=2)
    
    print(f"\nDataset generation complete!")
    print(f"Total runs: {len(dataset)}")
    print(f"Successful runs: {sum(1 for d in dataset if d['success'])}")
    print(f"CSV file: {csv_file}")
    print(f"JSON file: {json_file}")
    
    return csv_file, json_file

if __name__ == "__main__":
    generate_publication_dataset()
```

## Integration Examples

### Example 9: Jupyter Notebook Integration

```python
# music_theory_analysis.ipynb cell examples

# Cell 1: Setup
from llm_music_theory.core.runner import PromptRunner
from llm_music_theory.core.dispatcher import ModelDispatcher
import pandas as pd
import matplotlib.pyplot as plt
import json

runner = PromptRunner()
dispatcher = ModelDispatcher()

# Cell 2: Quick Analysis
question = "Q1b"
model = "gemini-2.0-flash-exp"

response = runner.run_analysis(
    question=question,
    model_name=model,
    encoded_type="musicxml",
    use_context=True
)

print(f"Analysis for {question} using {model}:")
print("=" * 50)
print(response)

# Cell 3: Compare Multiple Models
models = ["gemini-2.0-flash-exp", "gpt-4o", "claude-3-5-sonnet-20241022"]
results = {}

for model in models:
    try:
        response = runner.run_analysis(
            question=question,
            model_name=model,
            encoded_type="musicxml",
            use_context=True
        )
        results[model] = {
            "response": response,
            "length": len(response)
        }
    except Exception as e:
        results[model] = {"error": str(e)}

# Visualize response lengths
lengths = [results[model]["length"] for model in models if "length" in results[model]]
model_names = [model for model in models if "length" in results[model]]

plt.figure(figsize=(10, 6))
plt.bar(model_names, lengths)
plt.title("Response Length by Model")
plt.xlabel("Model")
plt.ylabel("Response Length (characters)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Cell 4: Format Comparison
formats = ["musicxml", "mei", "abc", "humdrum"]
format_results = {}

for format_type in formats:
    try:
        response = runner.run_analysis(
            question=question,
            model_name="gemini-2.0-flash-exp",
            encoded_type=format_type,
            use_context=True
        )
        format_results[format_type] = {
            "response": response,
            "length": len(response)
        }
    except Exception as e:
        format_results[format_type] = {"error": str(e)}

# Create DataFrame for analysis
df_data = []
for fmt in formats:
    if "length" in format_results[fmt]:
        df_data.append({
            "format": fmt,
            "length": format_results[fmt]["length"],
            "success": True
        })
    else:
        df_data.append({
            "format": fmt,
            "length": 0,
            "success": False
        })

df = pd.DataFrame(df_data)
print(df)
```

### Example 10: Web API Integration

```python
#!/usr/bin/env python3
"""
web_api.py - Simple web API for music theory analysis
"""

from flask import Flask, request, jsonify
from llm_music_theory.core.runner import PromptRunner
from llm_music_theory.core.dispatcher import ModelDispatcher
import logging

app = Flask(__name__)
runner = PromptRunner()
dispatcher = ModelDispatcher()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route("/api/models", methods=["GET"])
def get_available_models():
    """Get list of available models."""
    try:
        models = dispatcher.list_available_models()
        return jsonify({
            "success": True,
            "models": models
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/analyze", methods=["POST"])
def analyze_music():
    """Analyze music theory question."""
    try:
        data = request.get_json()
        
        # Validate required parameters
        required_params = ["question", "model"]
        for param in required_params:
            if param not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required parameter: {param}"
                }), 400
        
        # Optional parameters
        encoded_type = data.get("encoded_type")
        use_context = data.get("use_context", True)
        
        logger.info(f"Analysis request: {data}")
        
        # Run analysis
        response = runner.run_analysis(
            question=data["question"],
            model_name=data["model"],
            encoded_type=encoded_type,
            use_context=use_context
        )
        
        return jsonify({
            "success": True,
            "question": data["question"],
            "model": data["model"],
            "encoded_type": encoded_type,
            "use_context": use_context,
            "response": response,
            "response_length": len(response)
        })
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/batch", methods=["POST"])
def batch_analyze():
    """Batch analysis endpoint."""
    try:
        data = request.get_json()
        
        if "requests" not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'requests' parameter"
            }), 400
        
        results = []
        
        for i, req in enumerate(data["requests"]):
            try:
                response = runner.run_analysis(
                    question=req["question"],
                    model_name=req["model"],
                    encoded_type=req.get("encoded_type"),
                    use_context=req.get("use_context", True)
                )
                
                results.append({
                    "index": i,
                    "success": True,
                    "response": response,
                    "request": req
                })
                
            except Exception as e:
                results.append({
                    "index": i,
                    "success": False,
                    "error": str(e),
                    "request": req
                })
        
        return jsonify({
            "success": True,
            "total_requests": len(data["requests"]),
            "successful_requests": sum(1 for r in results if r["success"]),
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Batch analysis error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

# Usage example:
# curl -X POST http://localhost:5000/api/analyze \
#   -H "Content-Type: application/json" \
#   -d '{
#     "question": "Q1b",
#     "model": "gemini-2.0-flash-exp",
#     "encoded_type": "musicxml",
#     "use_context": true
#   }'
```

## Next Steps

After exploring these examples:

1. **Adapt for Your Use Case**: Modify the examples to fit your specific research or educational needs
2. **Scale Up**: Use the batch processing examples for larger studies
3. **Customize Analysis**: Extend the preprocessing and analysis pipeline
4. **Integrate**: Connect with your existing tools and workflows
5. **Share Results**: Contribute findings back to the community

## Related Documentation

- [Configuration](configuration.md) - Detailed usage information
- [API Reference](api-reference.md) - Complete programming interface
- [Research Guide](research.md) - Academic research guidance
- [Configuration](configuration.md) - System configuration options
