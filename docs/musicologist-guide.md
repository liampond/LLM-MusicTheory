# Musicologist's Guide to LLM-MusicTheory

*A non-technical guide for music experts working with AI language models*

## What This Project Does

LLM-MusicTheory is a research tool that tests how well AI language models (like ChatGPT, Claude, and Gemini) understand music theory concepts. Think of it as a way to give the same music theory question to multiple AI systems and compare their answers.

### The Big Picture

1. **You create** music theory questions and provide musical examples
2. **The system sends** these questions to different AI models  
3. **You analyze** how well each AI understood and answered the question
4. **You improve** the questions and examples based on what you learn

This helps us understand:
- Which AI models are best at music theory
- How different ways of presenting music affect AI understanding
- What kinds of music theory concepts are hardest for AI to grasp

## Your Role: Crafting Questions and Prompts

As a musicologist, your expertise is crucial for:

### 🎼 **Question Design**
- Creating meaningful music theory questions that test AI understanding
- Ensuring questions are pedagogically sound and cover important concepts
- Balancing difficulty levels appropriate for different learning objectives

### 📝 **Prompt Engineering** 
- Writing clear instructions that help AI models understand what you're asking
- Explaining musical concepts in ways that work well for AI systems
- Creating context that guides AI toward musically informed responses

### 🎵 **Musical Examples**
- Selecting appropriate musical excerpts that illustrate the concepts being tested
- Ensuring examples are clear and unambiguous
- Providing musical context that supports the analytical questions

## How the System Works

The LLM-MusicTheory system tests AI models on music theory tasks by combining your questions with musical examples. Here's the simplified workflow:

1. **Musical Data**: Musical examples are stored in various formats (MusicXML, MEI, ABC, Humdrum)
2. **Your Questions**: You write questions in plain English about music theory concepts
3. **Automatic Assembly**: The system combines your questions with the musical data and formatting instructions
4. **AI Analysis**: Complete prompts are sent to various AI models (ChatGPT, Claude, Gemini, etc.)
5. **Results**: You get back the AI's analysis or composition for comparison

### How Prompts Are Built

When you run a test, the system automatically assembles several components:

1. **Task Instructions** - Your main question (from `prompt.md` files)
2. **Guides** - Any contextual information or rules (optional)  
3. **Output Format** - Instructions for how the AI should respond (e.g., "provide MusicXML")
4. **Musical Data** - The actual encoded musical content

**You don't need to worry about technical formatting** - just write clear questions and the system handles combining everything.

## How to Get Started (Non-Technical)

### Step 1: Understanding the File Structure

The project organizes materials into clear folders:

```
data/
├── fux-counterpoint/          ← Default dataset for counterpoint studies
│   ├── prompts/
│   │   ├── prompt.md          ← Main question/task instructions
│   │   └── base/              ← Format-specific instructions
│   ├── encoded/               ← Musical examples in different formats
│   └── guides/                ← Optional contextual information
└── RCM6/                      ← Royal Conservatory exam questions dataset
    ├── prompts/
    │   ├── questions/
    │   │   ├── context/       ← Questions with musical examples
    │   │   └── no_context/    ← Text-only questions
    │   └── base/
    ├── encoded/
    └── guides/
```

### Step 2: Working with Datasets

The system supports different datasets:

**Fux-Counterpoint Dataset** (default)
- Focus on 16th-century counterpoint composition
- Single `prompt.md` file with base instructions
- Musical examples for AI to compose counterpoint

**RCM6 Dataset** 
- Royal Conservatory of Music Level 6 theory questions
- Questions exist in two versions:
  - **With Musical Context** (`prompts/questions/context/`) - Include musical notation
  - **Without Musical Context** (`prompts/questions/no_context/`) - Pure text questions
- ⚠️ **Current Status**: The RCM6 dataset has path resolution issues and may not work reliably

**Recommendation**: Focus on the fux-counterpoint dataset for reliable testing.

### Step 3: Understanding Music Formats

The system supports different ways of representing music:

- **MusicXML**: Industry standard, like a digital score
- **MEI**: Academic format with rich analytical markup  
- **ABC**: Simple text notation, like guitar tabs
- **Humdrum**: Research format for detailed analysis

*Don't worry about the technical details - just know that the same piece of music can be represented in different ways, and AI models might respond differently to each format.*

## Tested Working Examples

For your meeting tomorrow, here are verified working commands:

### ✅ Counterpoint Composition (Recommended)
```bash
# Basic counterpoint composition 
poetry run python -m llm_music_theory.cli.run_single \
  --file Fux_CantusFirmus \
  --model gemini \
  --datatype musicxml

# Compare different AI models
poetry run python -m llm_music_theory.cli.run_single \
  --file Fux_CantusFirmus \
  --model chatgpt \
  --datatype musicxml

# Test different musical formats
poetry run python -m llm_music_theory.cli.run_single \
  --file Fux_CantusFirmus \
  --model gemini \
  --datatype mei
```

### ⚠️ RCM6 Analysis (Experimental)
```bash
# This may not work due to path issues
poetry run python -m llm_music_theory.cli.run_single \
  --file Q1b \
  --model gemini \
  --dataset RCM6 \
  --context
```

## Working with the Command Line (Simple Version)

The system has a simple text interface. Here are the basic commands you'll use:

### Testing a Single Question

```bash
poetry run python -m llm_music_theory.cli.run_single \
  --file Q1b \
  --model gemini \
  --datatype musicxml \
  --context \
  --dataset RCM6
```

**What this means:**
- `--file Q1b`: Test question Q1b
- `--model gemini`: Use Google's Gemini AI
- `--datatype musicxml`: Use MusicXML format for the musical example
- `--context`: Include contextual guides with the question
- `--dataset RCM6`: Use the Royal Conservatory dataset

### Testing Different AI Models

```bash
# Test with Google Gemini
poetry run python -m llm_music_theory.cli.run_single --file Q1b --model gemini --context --dataset RCM6

# Test with OpenAI ChatGPT  
poetry run python -m llm_music_theory.cli.run_single --file Q1b --model chatgpt --context --dataset RCM6

# Test with Anthropic Claude
poetry run python -m llm_music_theory.cli.run_single --file Q1b --model claude --context --dataset RCM6
```

### Testing Counterpoint Composition

```bash
# Test counterpoint composition with the default dataset
poetry run python -m llm_music_theory.cli.run_single \
  --file Fux_CantusFirmus \
  --model gemini \
  --datatype musicxml
```

### Testing Without Musical Context

```bash
poetry run python -m llm_music_theory.cli.run_single \
  --file Q1b \
  --model gemini \
  --dataset RCM6
  # Note: No --context flag means text-only question
```

## Creating Your Own Questions

### Question File Structure

**For RCM6 Dataset Questions:**

Each question needs separate files for context vs. no-context versions:

**With Musical Context:**
```
data/RCM6/prompts/questions/context/musicxml/Q2a.txt
data/RCM6/prompts/questions/context/mei/Q2a.txt  
data/RCM6/prompts/questions/context/abc/Q2a.txt
data/RCM6/prompts/questions/context/humdrum/Q2a.txt
```

**Without Musical Context:**
```
data/RCM6/prompts/questions/no_context/Q2a.txt
```

**Corresponding Musical Examples:**
```
data/RCM6/encoded/musicxml/Q2a.musicxml
data/RCM6/encoded/mei/Q2a.mei
data/RCM6/encoded/abc/Q2a.abc
data/RCM6/encoded/humdrum/Q2a.krn
```

**For Fux-Counterpoint Dataset:**

Single prompt file with corresponding musical examples:
```
data/fux-counterpoint/prompts/prompt.md
data/fux-counterpoint/encoded/musicxml/YourFile.musicxml
data/fux-counterpoint/encoded/mei/YourFile.mei
```

### Writing Effective Questions

**Good Question Characteristics:**
- **Clear and specific**: "Identify the cadence types in measures 5-8"
- **Pedagogically sound**: Tests one concept at a time  
- **Appropriate difficulty**: Matches your learning objectives
- **Unambiguous**: Has a clear correct answer

**Question Template:**
```
Analyze the harmonic progression in the given musical score.

Focus on measures 1-4 and identify:
1. The key center
2. Roman numeral analysis for each chord
3. Any non-chord tones and their types
4. The cadence type at the end of the phrase

Provide your analysis in a clear, structured format with measure numbers.
```

*Note: You don't need to reference the musical data in your questions - the system automatically includes it*

### Prompt Engineering Tips

**For AI Success:**
- **Be explicit**: Don't assume the AI knows musical conventions
- **Provide structure**: Use numbered lists, clear sections
- **Give examples**: Show the format you want for answers
- **Set context**: Explain the musical style or period if relevant

**Example of Good Prompt Structure:**
```
You are analyzing a Bach chorale excerpt in common practice harmony.

Provide a Roman numeral analysis of the given musical score.

Instructions:
1. Identify the key (provide reasoning if ambiguous)
2. Analyze each chord using Roman numerals (I, ii, V7, etc.)
3. Mark any non-chord tones (PT = passing tone, NT = neighbor tone)
4. Identify the final cadence type

Format your response as:
Measure 1: I - vi - IV - V7
Measure 2: I (with PT in soprano)
etc.

Key: [Your analysis]
Cadence: [Type and location]
```

## Testing and Iterating on Your Work

### Quick Testing Workflow

1. **Create your question** in the appropriate text files
2. **Add your musical example** to the encoded folders
3. **Test with one AI model** to see if it works
4. **Refine the question** based on the response
5. **Test with multiple models** to compare responses
6. **Compare with/without context** to see how musical notation helps

### Evaluating AI Responses

**Look for:**
- **Accuracy**: Did the AI get the music theory correct?
- **Completeness**: Did it address all parts of your question?
- **Musical understanding**: Does the response show real comprehension?
- **Format compliance**: Did it follow your requested structure?

**Red flags:**
- Contradictory statements about the same musical passage
- Technical terminology used incorrectly
- Analysis that doesn't match the actual musical content
- Generic responses that could apply to any piece

## Common Workflow Example

Here's how you might develop and test a new question:

### 1. Initial Question Creation
```
Analyze the voice leading in this Bach chorale excerpt.

Focus on:
- Parallel motion between voices
- Resolution of dissonances  
- Approach to the final cadence
```

### 2. First Test
```bash
poetry run python -m llm_music_theory.cli.run_single --file Q2a --model chatgpt --context --dataset RCM6
```

### 3. Review Response
*AI response might be too vague or miss key points*

### 4. Refine Question
```
Analyze the voice leading in this four-voice Bach chorale excerpt from measure 1 to the final cadence.

Provide a detailed analysis addressing:

1. Voice Leading Quality:
   - Identify any parallel fifths or octaves (specify voices and measures)
   - Note any contrary motion between outer voices
   - Comment on smooth voice leading vs. leaps

2. Dissonance Treatment:
   - Identify all dissonances (specify voice, measure, beat)
   - Describe how each dissonance resolves
   - Note any suspensions or passing tones

3. Cadential Analysis:
   - Identify the cadence type in the final measures
   - Analyze the approach to the final chord
   - Comment on any voice leading patterns that strengthen the cadence

Format: Use measure numbers and voice names (Soprano, Alto, Tenor, Bass)
```

### 5. Test Refined Version
```bash
poetry run python -m llm_music_theory.cli.run_single --file Q2a --model chatgpt --context --dataset RCM6
```

### 6. Compare Across Models
```bash
# Test with different AI models
poetry run python -m llm_music_theory.cli.run_single --file Q2a --model gemini --context --dataset RCM6
poetry run python -m llm_music_theory.cli.run_single --file Q2a --model claude --context --dataset RCM6
```

## Understanding the Output

Results are saved in the `output/` folder with this structure:

```
output/
├── context/
│   ├── gpt-4o/
│   │   └── Q2a.txt
│   ├── gemini-2.0-flash-exp/
│   │   └── Q2a.txt
│   └── claude-3-5-sonnet-20241022/
│       └── Q2a.txt
└── no_context/
    └── gpt-4o/
        └── Q2a.txt
```

Each file contains the AI's complete response to your question. You can open these in any text editor to read and analyze the responses.

## Tips for Musicologists

### Start Simple
- Begin with straightforward harmonic analysis questions
- Test basic concepts before moving to complex analytical tasks
- Use familiar repertoire (Bach chorales, Mozart sonatas, etc.)

### Think Like a Teacher
- What would you ask a student to demonstrate understanding?
- How would you scaffold learning from simple to complex?
- What are the most common mistakes students make?

### Consider AI Limitations
- AI can't "hear" the music - only see the notation
- AI may struggle with ambiguous or contextual interpretations
- AI works best with explicit, structured questions

### Collaborate with Technical Team
- Share your musical insights about what works and what doesn't
- Explain why certain AI responses are problematic from a musicological perspective
- Suggest improvements based on pedagogical best practices

## Getting Help

**For immediate questions:**
- Check the `troubleshooting.md` file for common issues
- Look at existing questions in the `prompts/questions/` folder for examples

**For your first session:**
- Start by testing an existing question (like Q1b) to understand the workflow
- Try modifying an existing question before creating a new one
- Don't worry about the technical setup - focus on the musical content

**Remember:** Your musical expertise is the most important part of this project. The technical team can help with the computer aspects, but only you can ensure the questions are musically meaningful and pedagogically sound.

## What You Don't Need to Worry About

- **Programming**: You won't need to write code
- **Server setup**: The technical team handles API keys and configuration  
- **File formats**: You work with text files, others handle the technical conversion
- **AI model details**: You focus on questions, others handle the AI integration

Your job is to be the musical expert who ensures we're asking the right questions in the right way. The technology serves your musical and pedagogical expertise, not the other way around.
