# Research Documentation

Information for researchers using LLM-MusicTheory for academic studies.

## Overview

LLM-MusicTheory is designed to support empirical research into how large language models understand and analyze music theory concepts. This documentation provides guidance for conducting rigorous academic research.

## Research Applications

### 1. Model Comparison Studies

Compare how different LLM architectures handle music theory:

**Research Questions**:
- Which models best understand musical structure?
- How do different training approaches affect music theory comprehension?
- What are the strengths and weaknesses of each model family?

**Methodology**:
```bash
# Systematic model comparison
models=("gemini-2.0-flash-exp" "gpt-4o" "claude-3-5-sonnet-20241022" "deepseek-v3")
questions=("Q1b")  # Expand with your question set

for model in "${models[@]}"; do
  for question in "${questions[@]}"; do
    python -m llm_music_theory.cli.run_single \
      --question "$question" \
      --encoded_type musicxml \
      --model "$model" \
      --context
  done
done
```

### 2. Format Representation Studies

Investigate how music encoding affects model understanding:

**Research Questions**:
- Do models perform differently with MusicXML vs. ABC notation?
- How does format complexity affect analytical accuracy?
- Which formats best preserve musical semantics for LLMs?

**Methodology**:
```bash
# Format comparison study
formats=("musicxml" "mei" "abc" "humdrum")
model="gemini-2.0-flash-exp"

for format in "${formats[@]}"; do
  python -m llm_music_theory.cli.run_single \
    --question Q1b \
    --encoded_type "$format" \
    --model "$model" \
    --context
done
```

### 3. Context Effect Studies

Examine the impact of musical context on analysis quality:

**Research Questions**:
- How much does visual/encoded musical context improve analysis?
- What types of questions benefit most from context?
- Can models reason about music without explicit notation?

**Methodology**:
```bash
# Context vs no-context comparison
python -m llm_music_theory.cli.run_single \
  --question Q1b \
  --model gemini-2.0-flash-exp \
  --context

python -m llm_music_theory.cli.run_single \
  --question Q1b \
  --model gemini-2.0-flash-exp \
  --no-context
```

## Experimental Design Guidelines

### 1. Controlling Variables

**Model Variables**:
- Temperature settings (recommend 0.1 for consistency)
- Token limits (standardize across models)
- API version consistency
- Random seed control (where available)

**Content Variables**:
- Musical complexity (simple → complex progressions)
- Question difficulty (undergraduate → graduate level)
- Format complexity (ABC → MusicXML → MEI)
- Question type (analysis → evaluation → creation)

**Procedural Variables**:
- Question order randomization
- Multiple runs for reliability
- Blind evaluation of responses
- Inter-rater reliability measures

### 2. Sample Size Considerations

**Minimum Recommendations**:
- 30+ musical examples per condition
- 3+ runs per model/condition combination
- Multiple evaluators for subjective measures
- Statistical power analysis for effect sizes

**Practical Constraints**:
- API rate limits and costs
- Time for human evaluation
- Availability of expert evaluators
- Technical infrastructure limits

### 3. Validity Considerations

**Internal Validity**:
- Control for musical complexity
- Standardize prompt formatting
- Account for model training differences
- Minimize confounding variables

**External Validity**:
- Diverse musical styles and periods
- Representative question types
- Real-world analysis scenarios
- Cross-cultural musical examples

**Construct Validity**:
- Expert validation of questions
- Alignment with music theory pedagogy
- Appropriate difficulty levels
- Clear assessment criteria

## Data Collection Protocols

### 1. Automated Data Collection

Use batch processing for systematic data collection:

```python
# Example research data collection script
import json
from datetime import datetime
from llm_music_theory.cli.run_batch import run_batch_analysis

def collect_research_data():
    """Collect data for research study with proper metadata."""
    
    study_metadata = {
        "study_id": "format_comparison_2024",
        "timestamp": datetime.now().isoformat(),
        "researcher": "Your Name",
        "conditions": {
            "models": ["gemini-2.0-flash-exp", "gpt-4o", "claude-3-5-sonnet-20241022"],
            "formats": ["musicxml", "mei", "abc", "humdrum"],
            "questions": ["Q1b"],
            "context_conditions": [True, False]
        }
    }
    
    # Save metadata
    with open("study_metadata.json", "w") as f:
        json.dump(study_metadata, f, indent=2)
    
    # Collect data systematically
    for model in study_metadata["conditions"]["models"]:
        for format_type in study_metadata["conditions"]["formats"]:
            for context in study_metadata["conditions"]["context_conditions"]:
                run_condition(model, format_type, context)

def run_condition(model, format_type, context):
    """Run a single experimental condition."""
    # Implementation details...
    pass
```

### 2. Data Organization

Organize collected data for analysis:

```
research_data/
├── study_metadata.json
├── raw_responses/
│   ├── gemini-2.0-flash-exp/
│   │   ├── musicxml/
│   │   │   ├── context/
│   │   │   │   └── Q1b_run1.musicxml
│   │   │   └── no_context/
│   │   │       └── Q1b_run1.txt
│   │   └── mei/
│   │       └── ...
│   └── gpt-4o/
│       └── ...
├── coded_responses/
│   ├── accuracy_scores.csv
│   ├── error_categories.csv
│   └── qualitative_codes.csv
└── analysis/
    ├── statistical_analysis.R
    ├── visualizations/
    └── results_summary.md
```

### 3. Response Evaluation

Develop systematic evaluation criteria:

**Quantitative Measures**:
- Accuracy of harmonic analysis (% correct chords)
- Completeness of analysis (% elements identified)
- Consistency across runs (correlation coefficients)
- Response time/length metrics

**Qualitative Measures**:
- Depth of musical understanding
- Appropriate use of terminology
- Logical reasoning quality
- Novel insights or connections

**Evaluation Rubric Example**:
```
Harmonic Analysis Evaluation (0-5 scale):

1. Chord Identification
   - 5: All chords correctly identified
   - 4: 90%+ chords correct
   - 3: 75-89% chords correct
   - 2: 50-74% chords correct
   - 1: <50% chords correct

2. Roman Numeral Analysis
   - 5: Perfect functional analysis
   - 4: Minor functional errors
   - 3: Some functional understanding
   - 2: Limited functional understanding
   - 1: No functional understanding

[Continue for all evaluation dimensions...]
```

## Statistical Analysis Approaches

### 1. Descriptive Statistics

**Model Performance Comparison**:
- Mean accuracy scores by model
- Standard deviations and confidence intervals
- Distribution plots and box plots
- Correlation matrices

**Format Effect Analysis**:
- Performance differences across formats
- Effect sizes (Cohen's d, eta-squared)
- Pairwise comparisons with corrections
- Interaction effects

### 2. Inferential Statistics

**Appropriate Tests**:
- ANOVA for multi-group comparisons
- t-tests for paired comparisons
- Non-parametric tests for non-normal data
- Mixed-effects models for repeated measures

**Example Analysis Plan**:
```r
# R script example
library(tidyverse)
library(lme4)
library(ggplot2)

# Load data
data <- read_csv("accuracy_scores.csv")

# Mixed-effects model
model <- lmer(accuracy ~ model * format * context + 
              (1|question) + (1|evaluator), 
              data = data)

# Post-hoc comparisons
library(emmeans)
emmeans(model, pairwise ~ model)
```

### 3. Effect Size Interpretation

**Guidelines for Music Theory Research**:
- Small effect: d = 0.2 (subtle differences)
- Medium effect: d = 0.5 (noticeable differences)
- Large effect: d = 0.8 (substantial differences)

**Practical Significance**:
Consider both statistical and practical significance:
- 5% accuracy difference may be statistically significant but not pedagogically meaningful
- Qualitative differences in reasoning may be more important than quantitative scores

## Ethical Considerations

### 1. Academic Integrity

**Transparency Requirements**:
- Report all models and versions tested
- Disclose any failed experiments or null results
- Share data and analysis code when possible
- Acknowledge limitations and biases

**Reproducibility Standards**:
- Document exact model settings used
- Provide detailed methodology descriptions
- Share prompt templates and evaluation rubrics
- Archive model responses for verification

### 2. Bias and Limitations

**Potential Biases**:
- Training data bias in models
- Researcher bias in evaluation
- Cultural bias in musical examples
- Format bias in encoding choices

**Mitigation Strategies**:
- Use diverse musical examples
- Multiple independent evaluators
- Blind evaluation procedures
- Cross-validation with human experts

### 3. Responsible Reporting

**Balanced Presentation**:
- Report both strengths and weaknesses
- Avoid overgeneralization from limited samples
- Discuss implications for music education
- Consider broader societal impacts

## Publication Guidelines

### 1. Methodology Section

Include comprehensive details about:
- Experimental design and rationale
- Model specifications and settings
- Question selection and validation
- Evaluation procedures and criteria
- Statistical analysis methods

### 2. Results Presentation

**Quantitative Results**:
- Tables with descriptive statistics
- Visualizations of key findings
- Effect sizes with confidence intervals
- Statistical test results and p-values

**Qualitative Results**:
- Representative response examples
- Thematic analysis of error types
- Illustrative quotes from model responses
- Comparative analysis across conditions

### 3. Discussion Framework

**Key Discussion Points**:
- Implications for music theory pedagogy
- Insights into model capabilities and limitations
- Comparison with existing literature
- Future research directions
- Practical applications

## Collaboration Opportunities

### 1. Multi-Institutional Studies

**Benefits of Collaboration**:
- Larger sample sizes
- Diverse perspectives and expertise
- Resource sharing and cost reduction
- Enhanced credibility and impact

**Coordination Requirements**:
- Standardized protocols
- Shared data formats
- Common evaluation criteria
- Clear authorship agreements

### 2. Interdisciplinary Research

**Potential Collaborations**:
- Computer Science: Model development and analysis
- Cognitive Science: Human-AI comparison studies
- Music Education: Pedagogical effectiveness studies
- Digital Humanities: Cultural and historical analysis

## Funding and Resources

### 1. Grant Opportunities

**Relevant Funding Agencies**:
- NSF (Computer and Information Science and Engineering)
- NEH (Digital Humanities Advancement Grants)
- IMLS (National Leadership Grants)
- University internal research funds

**Budget Considerations**:
- API costs for large-scale studies
- Human evaluation time and expertise
- Computing resources and storage
- Conference presentation and publication fees

### 2. Resource Sharing

**Community Resources**:
- Shared question databases
- Evaluation rubric libraries
- Analysis code repositories
- Best practices documentation

## Next Steps for Researchers

1. **Start Small**: Begin with pilot studies to refine methodology
2. **Seek Collaboration**: Connect with other researchers in the field
3. **Document Everything**: Maintain detailed research logs and protocols
4. **Share Results**: Contribute findings to the broader research community
5. **Iterate and Improve**: Use initial findings to design better studies

## Related Documentation

- [Examples](examples.md) - Practical usage examples for research
- [API Reference](api-reference.md) - Programming interface for automation
- [Development Guide](development.md) - Contributing improvements to the system
- [Configuration](configuration.md) - System setup for research
