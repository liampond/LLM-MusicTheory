# Troubleshooting Guide

Common issues and their solutions when using LLM-MusicTheory.

## Installation Issues

### Poetry Installation Problems

**Issue**: `poetry: command not found`
```bash
# Solution: Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"
```

**Issue**: Poetry uses wrong Python version
```bash
# Solution: Configure Poetry to use correct Python
poetry env use python3.11
poetry install
```

### Dependency Issues

**Issue**: Package conflicts during installation
```bash
# Solution: Clear Poetry cache and reinstall
poetry cache clear --all pypi
rm poetry.lock
poetry install
```

## API Key Issues

### Missing API Keys

**Issue**: `API key not found` errors
```bash
# Check if environment variables are set
echo $GOOGLE_API_KEY
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
```

**Solution**: Set the required environment variables
```bash
# Temporary (current session only)
export GOOGLE_API_KEY="your-key-here"

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export GOOGLE_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### Invalid API Keys

**Issue**: `401 Unauthorized` or `403 Forbidden` errors

**Solutions**:
1. Verify the API key is correct (no extra spaces)
2. Check the key has necessary permissions
3. Ensure you haven't exceeded rate limits
4. For new keys, wait a few minutes for activation

### Rate Limiting

**Issue**: `429 Too Many Requests` errors

**Solutions**:
1. Add delays between requests
2. Use a different model/provider
3. Check your API plan limits
4. Implement exponential backoff (future feature)

## File and Path Issues

### Question Files Not Found

**Issue**: `Question file not found: Q1b`
```bash
# Check if question files exist
ls src/llm_music_theory/prompts/questions/no_context/
ls src/llm_music_theory/prompts/questions/context/
```

**Solution**: Verify question file structure:
```
src/llm_music_theory/prompts/questions/
├── no_context/
│   └── Q1b.txt
└── context/
    ├── musicxml/
    │   └── Q1b.txt
    ├── mei/
    │   └── Q1b.txt
    ├── abc/
    │   └── Q1b.txt
    └── humdrum/
        └── Q1b.txt
```

### Encoded Files Not Found

**Issue**: `Encoded file not found: Q1b.musicxml`
```bash
# Check if encoded files exist
ls src/llm_music_theory/encoded/musicxml/
ls src/llm_music_theory/encoded/mei/
ls src/llm_music_theory/encoded/abc/
ls src/llm_music_theory/encoded/humdrum/
```

**Solution**: Ensure encoded files are in the correct directories:
```
src/llm_music_theory/encoded/
├── musicxml/
│   └── Q1b.musicxml
├── mei/
│   └── Q1b.mei
├── abc/
│   └── Q1b.abc
└── humdrum/
    └── Q1b.krn
```

### Permission Issues

**Issue**: `Permission denied` when writing output files
```bash
# Check output directory permissions
ls -la output/

# Solution: Fix permissions
chmod 755 output/
chmod 644 output/*.txt
```

## Runtime Issues

### Import Errors

**Issue**: `ModuleNotFoundError: No module named 'llm_music_theory'`

**Solutions**:
1. Ensure you're in the Poetry environment:
   ```bash
   poetry shell
   ```
2. Install in development mode:
   ```bash
   poetry install
   ```
3. Check Python path:
   ```bash
   python -c "import sys; print(sys.path)"
   ```

### Model-Specific Issues

**Google Gemini Issues**:
- Ensure you have the latest `google-generativeai` package
- Some models may have regional restrictions
- Check quota limits in Google AI Studio

**OpenAI Issues**:
- Verify model names (e.g., `gpt-4o` not `gpt-4-omni`)
- Check API plan supports the requested model
- Monitor usage dashboard for limits

**Anthropic Issues**:
- Ensure correct model naming convention
- Check message length limits
- Verify API access for your region

### Memory Issues

**Issue**: Out of memory errors with large files

**Solutions**:
1. Use smaller batch sizes
2. Process files individually
3. Increase system memory
4. Use streaming for large outputs

## Output Issues

### Wrong File Extensions

**Issue**: Output files saved as `.txt` instead of input format

This should be fixed in the latest version. If you still see this:
```bash
# Check your version
git log --oneline -5

# Update to latest
git pull origin main
poetry install
```

### Empty Output Files

**Issue**: Output files are created but empty

**Debugging steps**:
1. Check API response in logs
2. Verify model is responding
3. Test with a simpler question
4. Check network connectivity

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python -m llm_music_theory.cli.run_single --question Q1b --model gemini-2.0-flash-exp
```

## Performance Issues

### Slow Response Times

**Causes and Solutions**:
1. **Large prompts**: Use `--no-context` for faster responses
2. **Model choice**: Some models are slower (o1-preview vs gpt-4o-mini)
3. **Network**: Check internet connection
4. **API load**: Try different times of day

### High API Costs

**Cost optimization**:
1. Use smaller models for testing (`gpt-4o-mini`, `gemini-2.0-flash-exp`)
2. Use `--no-context` when musical context isn't needed
3. Batch related questions together
4. Monitor usage dashboards

## Getting More Help

### Enable Debug Logging
```bash
export LOG_LEVEL=DEBUG
python -m llm_music_theory.cli.run_single [your-command]
```

### Check System Information
```bash
# Python version
python --version

# Poetry version
poetry --version

# Package versions
poetry show

# Environment variables
env | grep -E "(GOOGLE|OPENAI|ANTHROPIC)_API_KEY"
```

### Report Issues

If you encounter a bug:
1. Check if it's a known issue in [CHANGELOG.md](../../CHANGELOG.md)
2. Create a minimal reproduction case
3. Include system information and error logs
4. Submit an issue with complete details

### Community Support

- Check existing [documentation](../)
- Review [examples](examples.md)
- Consult [API reference](api-reference.md)
- See [development guide](development.md) for advanced topics
