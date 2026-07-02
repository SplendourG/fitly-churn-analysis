# Contributing to Fit.ly Churn Analysis

Thank you for your interest in contributing! This document outlines the process for contributing code, reporting issues, and improving the project.

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

## How to Contribute

### Reporting Issues

1. Check if the issue already exists in [GitHub Issues](https://github.com/SplendourG/fitly-churn-analysis/issues).
2. If not, create a new issue with:
   - A clear title
   - Detailed description of the problem
   - Steps to reproduce (if applicable)
   - Environment details (Python version, OS, etc.)
   - Error messages or logs

### Submitting Code Changes

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/your-username/fitly-churn-analysis.git
   cd fitly-churn-analysis
   ```

2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes and test:**
   ```bash
   pytest tests/ -v
   ```

4. **Follow code style:**
   ```bash
   black src tests
   flake8 src tests
   ```

5. **Commit with clear messages:**
   ```bash
   git add .
   git commit -m "Add feature: description of change"
   ```

6. **Push and open a Pull Request:**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Style

Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with:
- Max line length: 88 characters
- PEP 257 docstrings
- Type hints for function signatures

## Testing

```bash
pytest tests/ -v --cov=src
```

## Questions?

Open an issue or discussion. We're here to help!
