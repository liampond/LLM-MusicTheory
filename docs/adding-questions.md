# Adding Questions

Learn how to add your own music theory questions to the LLM-MusicTheory system.

## Question Structure Overview

Questions in LLM-MusicTheory have two variants:
- **No Context**: Questions without musical notation
- **Context**: Questions that include encoded musical content

Both variants should test the same concept but approach it differently.

## Directory Structure

Questions are organized in this structure:
```
data/RCM6/prompts/questions/
├── no_context/
│   └── your_question.txt
└── context/
    ├── musicxml/
    │   └── your_question.txt
    ├── mei/
    │   └── your_question.txt
    ├── abc/
    │   └── your_question.txt
    └── humdrum/
        └── your_question.txt
```

## Step-by-Step Guide

### 1. Prepare Your Musical Content

First, create encoded versions of your musical example in all supported formats:

```bash
# Create directories for your question (use appropriate dataset)
mkdir -p data/RCM6/encoded/musicxml
mkdir -p data/RCM6/encoded/mei
mkdir -p data/RCM6/encoded/abc
mkdir -p data/RCM6/encoded/humdrum
```

**Example: Adding question Q2a**

Save your musical content in each format:
- `data/RCM6/encoded/musicxml/Q2a.musicxml`
- `data/RCM6/encoded/mei/Q2a.mei`
- `data/RCM6/encoded/abc/Q2a.abc`
- `- `data/RCM6/encoded/humdrum/Q2a.krn`

### Step 2: Create Question Prompts

Create `data/RCM6/prompts/questions/no_context/Q2a.txt`:`

### 2. Create the No-Context Question

Create `src/llm_music_theory/prompts/questions/no_context/Q2a.txt`:

```text
Analyze the harmonic progression in the following musical excerpt. Identify:

1. The key and any modulations
2. Roman numeral analysis of each chord
3. Non-chord tones and their types
4. Cadence types and their locations
5. Any notable voice-leading patterns

Provide your analysis in a clear, structured format with measure numbers.

[Musical excerpt would typically be described in text here, or this would be a purely theoretical question]
```

### 3. Create Context Questions for Each Format

Create format-specific questions that reference the encoded content:

**MusicXML version** (`data/RCM6/prompts/questions/context/musicxml/Q2a.txt`):
```text
Given the musical score in MusicXML format below, provide a detailed harmonic analysis.

{encoded_content}

Analyze this musical excerpt and identify:

1. The key and any modulations
2. Roman numeral analysis of each chord
3. Non-chord tones and their types (passing tones, neighbor tones, suspensions, etc.)
4. Cadence types and their locations
5. Any notable voice-leading patterns

Provide your analysis in a clear, structured format with specific measure numbers and beat references. Explain your reasoning for ambiguous passages.
```

**MEI version** (`data/RCM6/prompts/questions/context/mei/Q2a.txt`):
```text
Given the musical score in MEI (Music Encoding Initiative) format below, provide a detailed harmonic analysis.

{encoded_content}

Analyze this musical excerpt and identify:

1. The key and any modulations
2. Roman numeral analysis of each chord
3. Non-chord tones and their types (passing tones, neighbor tones, suspensions, etc.)
4. Cadence types and their locations
5. Any notable voice-leading patterns

Use the structural information available in the MEI encoding to support your analysis. Provide specific measure numbers and beat references.
```

**ABC version** (`data/RCM6/prompts/questions/context/abc/Q2a.txt`):
```text
Given the musical score in ABC notation format below, provide a detailed harmonic analysis.

{encoded_content}

Analyze this musical excerpt and identify:

1. The key and any modulations
2. Roman numeral analysis of each chord
3. Non-chord tones and their types (passing tones, neighbor tones, suspensions, etc.)
4. Cadence types and their locations
5. Any notable voice-leading patterns

Reference the ABC notation structure in your analysis. Provide measure numbers and note positions as they appear in the ABC format.
```

**Humdrum version** (`data/RCM6/prompts/questions/context/humdrum/Q2a.txt`):
```text
Given the musical score in Humdrum format below, provide a detailed harmonic analysis.

{encoded_content}

Analyze this musical excerpt and identify:

1. The key and any modulations
2. Roman numeral analysis of each chord
3. Non-chord tones and their types (passing tones, neighbor tones, suspensions, etc.)
4. Cadence types and their locations
5. Any notable voice-leading patterns

Use the spine structure and analytical capabilities of the Humdrum format to inform your analysis. Reference specific data records and spines in your response.
```

## Question Design Best Practices

### 1. Clear Learning Objectives

Each question should have clear, measurable learning objectives:

```text
Learning Objectives:
- Identify chord progressions in common practice harmony
- Recognize and classify non-chord tones
- Analyze cadential patterns
- Apply Roman numeral analysis conventions
```

### 2. Appropriate Difficulty Level

Consider your target audience:
- **Undergraduate**: Basic chord identification, simple progressions
- **Graduate**: Complex chromatic harmony, advanced analysis
- **Research**: Novel analytical approaches, comparative studies

### 3. Comprehensive Coverage

Design questions that test multiple aspects:
- **Recognition**: Identify musical elements
- **Analysis**: Explain harmonic/melodic relationships
- **Evaluation**: Compare different interpretations
- **Application**: Apply theoretical concepts

### 4. Format-Specific Considerations

Tailor your questions to leverage each format's strengths:

**MusicXML**: Rich metadata, multiple voices, complex notation
```text
Analyze the voice-leading between soprano and bass voices, paying attention to the chord symbols and figured bass markings encoded in the MusicXML.
```

**MEI**: Scholarly encoding, analytical markup
```text
Examine any analytical annotations embedded in the MEI encoding and provide additional harmonic analysis.
```

**ABC**: Compact notation, folk/traditional music
```text
Identify the modal characteristics suggested by the ABC key signature and note patterns.
```

**Humdrum**: Analytical spine structure
```text
Using the harmonic analysis spine (**harm), verify and extend the provided Roman numeral analysis.
```

## Advanced Question Types

### 1. Comparative Questions

Questions that ask models to compare different aspects:

```text
Compare the harmonic rhythm in measures 1-4 versus measures 5-8. How does the composer use different chord durations to create tension and release?
```

### 2. Style Analysis Questions

Questions focusing on compositional style:

```text
Identify features that are characteristic of [Baroque/Classical/Romantic] style in this excerpt. Support your analysis with specific musical examples.
```

### 3. Error Detection Questions

Questions that include intentional errors:

```text
The following Roman numeral analysis contains three errors. Identify them and provide the correct analysis:

[Provided analysis with intentional mistakes]
```

### 4. Creative Application Questions

Questions that ask for extensions or variations:

```text
Propose two alternative harmonizations for the given melody. Explain how each harmonization creates a different musical character.
```

## Testing Your Questions

### 1. Validation Testing

Test your new questions with different models:

```bash
# Test with different models
for model in "gemini" "chatgpt" "claude"; do
  echo "Testing Q2a with $model..."
  poetry run python -m llm_music_theory.cli.run_single \
    --file Q2a \
    --datatype musicxml \
    --model "$model" \
    --context \
    --dataset RCM6
done
```

### 2. Format Comparison

Test how models handle different music formats:

```bash
# Test different formats
for format in "musicxml" "mei" "abc" "humdrum"; do
  echo "Testing Q2a with $format format..."
  poetry run python -m llm_music_theory.cli.run_single \
    --file Q2a \
    --datatype "$format" \
    --model gemini \
    --context \
    --dataset RCM6
done
```

### 3. Context vs No-Context

Compare context and no-context responses:

```bash
# With context
poetry run python -m llm_music_theory.cli.run_single \
  --file Q2a \
  --datatype musicxml \
  --model gemini \
  --context \
  --dataset RCM6

# Without context
poetry run python -m llm_music_theory.cli.run_single \
  --file Q2a \
  --model gemini \
  --dataset RCM6
```

## Quality Assurance

### 1. Question Review Checklist

- [ ] Clear, specific instructions
- [ ] Appropriate difficulty level
- [ ] No ambiguous terminology
- [ ] Consistent with learning objectives
- [ ] Format-specific optimizations
- [ ] No encoding-specific errors

### 2. Content Validation

- [ ] Musical content is accurate
- [ ] All format encodings are equivalent
- [ ] File extensions match format types
- [ ] No syntax errors in encoded files

### 3. Response Evaluation

Review model responses for:
- [ ] Accuracy of musical analysis
- [ ] Appropriate use of terminology
- [ ] Clear structure and organization
- [ ] Evidence of understanding the format

## Question Categories

Consider organizing questions into categories:

### Core Theory
- `Q1a`, `Q1b`: Species counterpoint
- `Q2a`, `Q2b`: Harmonic analysis
- `Q3a`, `Q3b`: Voice leading

### Applied Analysis
- `Q4a`, `Q4b`: Formal analysis
- `Q5a`, `Q5b`: Style analysis
- `Q6a`, `Q6b`: Performance analysis

### Advanced Topics
- `Q7a`, `Q7b`: Atonal analysis
- `Q8a`, `Q8b`: Jazz harmony
- `Q9a`, `Q9b`: Contemporary techniques

## Documentation

Document your questions in a catalog:

```markdown
# Question Catalog

## Q2a: Harmonic Analysis - Bach Chorale
- **Level**: Undergraduate
- **Topic**: Common practice harmony
- **Skills**: Chord identification, Roman numeral analysis
- **Duration**: 15-20 minutes
- **Musical Content**: Bach chorale excerpt (BWV 123, mm. 1-8)
```

## Next Steps

After adding questions:

1. **Test thoroughly** with multiple models and formats
2. **Document** in your question catalog
3. **Share** with colleagues for peer review
4. **Iterate** based on model responses and feedback
5. **Consider** adding to the main question database

## Related Documentation

- [Configuration](configuration.md) - Advanced prompt engineering
- [Configuration](configuration.md) - System configuration options
- [Examples](examples.md) - See existing question examples
- [API Reference](api-reference.md) - Programming interface for questions
