# Contributing to Madrid Real Estate Analytics Pipeline

First off, thank you for considering contributing to this project! 🎉

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Your environment details (OS, Python version, etc.)
- Relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- A clear and descriptive title
- Detailed description of the proposed functionality
- Why this enhancement would be useful
- Possible implementation approach

### Pull Requests

1. Fork the repo and create your branch from `main`
2. Make your changes following the code style guidelines
3. Add tests if applicable
4. Update documentation as needed
5. Ensure all tests pass
6. Submit a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/idealista-analytics-pipeline.git
cd idealista-analytics-pipeline

# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up pre-commit hooks (if available)
pre-commit install
```

## Code Style Guidelines

### Python
- Follow PEP 8
- Use type hints where appropriate
- Document functions with docstrings
- Keep functions focused and small

### SQL (dbt)
- Use lowercase for keywords
- Indent with 4 spaces
- Use CTEs for readability
- Comment complex logic

### Git Commits
- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, etc.)
- Keep commits atomic and focused

Example:
```
Add zone analysis metrics to intermediate model
Fix price deviation calculation in enriched model
Update README with new setup instructions
```

## Testing

```bash
# Run Python tests
pytest tests/

# Run dbt tests
cd dbt
dbt test

# Validate Airflow DAGs
airflow dags test idealista_analytics_pipeline 2024-01-01
```

## Questions?

Feel free to open an issue for any questions or discussions!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
