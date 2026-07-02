# Fit.ly Churn Analysis

A comprehensive data analysis project to identify factors associated with subscriber churn and recommend retention strategies for Fit.ly.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Usage](#usage)
- [Data](#data)
- [Results](#results)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project analyzes customer churn at Fit.ly by combining three data sources:

- **Account data**: Customer subscription plans, pricing, and churn status
- **Product activity**: User event tracking and engagement metrics
- **Customer support**: Ticket history, resolution times, and data deletion requests

### Key Questions

1. What is the baseline retention rate, and how does it vary by plan?
2. Is there a relationship between engagement and churn?
3. How does support ticket volume and resolution time impact churn?
4. Do data deletion requests signal imminent churn?
5. What actions can reduce churn in the next quarter?

### Key Findings

- Churn varies significantly by subscription plan
- Low-engagement customers are at higher churn risk
- High support volume and unresolved tickets correlate with churn
- Data deletion requests are a strong warning signal for churn

## Project Structure

```
fitly-churn-analysis/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── setup.py
├── data/
│   ├── raw/
│   └── processed/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── data_loading.py
│   ├── data_processing.py
│   ├── visualization.py
│   └── reporting.py
├── tests/
│   ├── __init__.py
│   ├── test_data_loading.py
│   └── test_data_processing.py
├── .github/
│   └── workflows/
│       └── tests.yml
└── outputs/
```

## Setup & Installation

### Prerequisites

- Python 3.8+
- pip or conda

### Local Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/SplendourG/fitly-churn-analysis.git
   cd fitly-churn-analysis
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Place raw data files in `data/raw/`:**

   - `da_fitly_account_info.csv`
   - `da_fitly_user_activity.csv`
   - `da_fitly_customer_support.csv`

## Usage

### Run the Full Analysis

```bash
python src/main.py
```

This will:
1. Load and clean all three data sources
2. Aggregate data to customer level
3. Generate summary statistics
4. Create visualizations
5. Write a markdown report to `outputs/fitly_churn_report.md`

### Output Files

After running the analysis:

- **CSV files:** Customer dataset, summaries, validation metrics
- **Visualizations:** 5 PNG charts showing key insights
- **Report:** Markdown report with findings and recommendations

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Reporting issues
- Submitting code changes
- Code style and testing requirements

## License

MIT License — see [LICENSE](LICENSE) file for details.
