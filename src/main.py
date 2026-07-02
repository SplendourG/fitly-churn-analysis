"""Main entry point for Fit.ly churn analysis.

Usage:
    python src/main.py

This script:
1. Loads and cleans data from three CSV files
2. Aggregates to customer level
3. Generates summary statistics
4. Creates visualizations
5. Writes an executive report

Outputs are saved to the `outputs/` directory.
"""
from pathlib import Path

from data_loading import load_and_clean
from data_processing import create_summaries
from visualization import create_visuals
from reporting import write_report


def main() -> None:
    """Run the complete churn analysis pipeline."""
    # Define output directory
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True, parents=True)

    # Load and clean data
    print("Loading and cleaning data...")
    data = load_and_clean(data_dir=Path("data/raw"))
    print(f"  Loaded {len(data['customer'])} customers")

    # Create summary tables
    print("Creating summary tables...")
    summaries = create_summaries(
        data["customer"],
        data["activity"],
        data["support"],
    )

    # Save clean data and summaries
    print("Saving outputs...")
    data["customer"].to_csv(
        output_dir / "clean_customer_level_dataset.csv", index=False
    )
    data["validation"].to_csv(output_dir / "validation_summary.csv", index=False)
    for name, summary in summaries.items():
        summary.to_csv(output_dir / f"{name}.csv", index=False)

    # Create visualizations
    print("Creating visualizations...")
    create_visuals(data["customer"], summaries, output_dir)

    # Write report
    print("Writing report...")
    write_report(summaries, output_dir)

    # Print summary to console
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\nOutputs saved to: {output_dir.absolute()}\n")
    print("Overall metrics:")
    print(summaries["overall"].to_string(index=False))
    print("\nChurn by plan:")
    print(summaries["plan_summary"].to_string(index=False))
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
