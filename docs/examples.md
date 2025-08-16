# 🎯 Examples

Practical examples and tutorials for the LLM-MusicTheory toolkit. Start here to learn by doing!

## 🚀 Quick Start Examples

Perfect for getting started and understanding the basics.

### Basic Usage Examples

| Example | Purpose | Complexity |
|---------|---------|------------|
| **[`basic_single_prompt.py`](#basic-single-prompt)** | Execute one prompt | ⭐ Beginner |
| **[`basic_batch_processing.py`](#basic-batch-processing)** | Run multiple prompts | ⭐ Beginner |
| **[`model_comparison.py`](#model-comparison)** | Compare different LLMs | ⭐⭐ Intermediate |

### Advanced Examples

| Example | Purpose | Complexity |
|---------|---------|------------|
| **[`context_experiment.py`](#context-experiment)** | Context vs no-context analysis | ⭐⭐ Intermediate |
| **[`parameter_tuning.py`](#parameter-tuning)** | Temperature and token optimization | ⭐⭐⭐ Advanced |
| **[`custom_provider.py`](#custom-provider)** | Add your own LLM | ⭐⭐⭐ Advanced |

### Analysis & Research

| Example | Purpose | Complexity |
|---------|---------|------------|
| **[`response_analysis.py`](#response-analysis)** | Analyze LLM outputs | ⭐⭐ Intermediate |
| **[`cost_calculator.py`](#cost-calculator)** | Estimate API costs | ⭐⭐ Intermediate |
| **[`research_pipeline.py`](#research-pipeline)** | Full research workflow | ⭐⭐⭐ Advanced |

## 🛠 Prerequisites

```bash
# 1. Install the project
git clone https://github.com/liampond/LLM-MusicTheory.git
cd LLM-MusicTheory
poetry install

# 2. Set up API keys
cp .env.example .env
# Edit .env with your actual API keys

# 3. Test installation
poetry run pytest tests/test_models.py -v
```

## 📚 Example Categories

### 1. Basic Usage Examples

#### Single Prompt Execution
```python
# examples/basic_usage.py
from llm_music_theory.core.runner import PromptRunner
from llm_music_theory.core.dispatcher import get_llm

# Simple execution
llm = get_llm("chatgpt")
runner = PromptRunner(
    model=llm,
    file_id="Q1b",
    datatype="mei",
    context=True
)
response = runner.run()
print(response)
```

#### Model Comparison
```python
# examples/model_comparison.py
models = ["chatgpt", "claude", "gemini", "deepseek"]
results = {}

for model_name in models:
    llm = get_llm(model_name)
    runner = PromptRunner(model=llm, file_id="Q1a", datatype="mei")
    results[model_name] = runner.run()

# Compare responses
for model, response in results.items():
    print(f"{model}: {response[:100]}...")
```

### 2. Advanced Workflow Examples

#### Batch Processing
```python
# examples/batch_processing.py
questions = ["Q1a", "Q1b"]
datatypes = ["mei", "musicxml"]
models = ["chatgpt", "claude"]

for model_name in models:
    for question in questions:
        for datatype in datatypes:
            # Process each combination
            runner = PromptRunner(
                model=get_llm(model_name),
                file_id=question,
                datatype=datatype,
                save=True
            )
            runner.run()
```

#### Context Analysis
```python
# examples/context_analysis.py
def compare_context_modes(question, datatype, model):
    """Compare responses with and without context."""
    
    # With context
    runner_context = PromptRunner(
    model=get_llm(model),
    file_id=question,
        datatype=datatype,
        context=True
    )
    
    # Without context  
    runner_no_context = PromptRunner(
    model=get_llm(model),
    file_id=question,
        datatype=datatype,
        context=False
    )
    
    return {
        'with_context': runner_context.run(),
        'without_context': runner_no_context.run()
    }
```

### 3. Integration Examples

#### Custom Model Integration
```python
# examples/custom_model.py
from llm_music_theory.models.base import LLMInterface, PromptInput

class MyCustomLLM(LLMInterface):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def query(self, input: PromptInput) -> str:
        # Implement your custom LLM integration
        return "Custom model response"

# Register and use
custom_llm = MyCustomLLM("your-api-key")
runner = PromptRunner(model=custom_llm, file_id="Q1a", datatype="mei")
```

## 🔧 Development Examples

### Testing New Features
```python
# examples/test_new_feature.py
import pytest
from llm_music_theory.core.runner import PromptRunner

def test_example():
    """Example of how to test new functionality."""
    runner = PromptRunner(model=MockLLM(), file_id="Q1a", datatype="mei")
    response = runner.run()
    assert len(response) > 0
```

### Performance Measurement
```python
# examples/performance_metrics.py
import time
import time
def run_benchmark():
    """Benchmark prompt execution time."""
    start = time.time()
    runner = PromptRunner(model=get_llm("chatgpt"), file_id="Q1a", datatype="mei")
    response = runner.run()
    duration = time.time() - start
    print({"response_time": duration, "response_length": len(response)})
```

## 💡 Best Practices Demonstrated

### 1. Error Handling
```python
try:
    runner = PromptRunner(...)
    response = runner.run()
except FileNotFoundError:
    print("Required data files not found")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### 2. Configuration Management
```python
from llm_music_theory.config.settings import get_settings

settings = get_settings()
runner = PromptRunner(
    model=get_llm(settings.default_model),
    temperature=settings.default_temperature,
    ...
)
```

### 3. Resource Management
```python
with PromptRunner(...) as runner:
    response = runner.run()
    # Automatic cleanup
```

## 📊 Expected Outputs

### Example Output Structure
```
outputs/
├── ChatGPT/
│   ├── fux-counterpoint__Q1a_mei_context.txt
│   └── fux-counterpoint__Q1a_mei_context.input.json
├── Claude/
│   └── ...
└── analysis/
    ├── comparison_report.html
    └── performance_metrics.json
```

### Sample Response Format
```json
{
  "model": "chatgpt",
    "file_id": "Q1b",
  "datatype": "mei",
  "context": true,
  "timestamp": "2025-01-08T10:30:00Z",
  "response": "The chord progression shows...",
  "metadata": {
    "temperature": 0.0
  }
}
```

## 🎯 Learning Path

### For Beginners
1. Start with `basic_usage.py`
2. Try `model_comparison.py` 
3. Experiment with `parameter_tuning.py`

### For Advanced Users
1. Explore `batch_processing.py`
2. Study `custom_model.py`
3. Implement your own analysis scripts

### For Developers
1. Review `test_new_feature.py`
2. Understand `performance_metrics.py`
3. Create custom integration examples

## 🤝 Contributing Examples

To contribute a new example:

1. **Create** a new `.py` file in the appropriate category
2. **Include** clear comments and docstrings
3. **Add** a brief description to this README
4. **Test** that your example runs successfully
5. **Submit** a pull request

### Example Template
```python
"""
Brief description of what this example demonstrates.

Usage:
    poetry run python examples/your_example.py

Requirements:
    - API key for [specific provider]
    - Data files in data/ directory
"""

# Your example code here
```

---

*Need help with examples? [Open an issue](https://github.com/liampond/LLM-MusicTheory/issues) with the `examples` label.*
