from pathlib import Path
import csv
import re
import statistics


DATASET_DIR = Path("data/raw/SDALLE")

HEADER_LINE = 6
SAMPLING_RATE_LINE = 7
DATA_START_LINE = 8


def read_csv_rows(file_path):
    """Read the CSV file into rows."""
    with open(
        file_path,
        "r",
        encoding="utf-8-sig",
        errors="replace",
        newline=""
    ) as f:
        return list(csv.reader(f))


def parse_trial(file_path):
    """Parse one SDALLE trial."""

    rows = read_csv_rows(file_path)

    if len(rows) < DATA_START_LINE:
        raise ValueError(
            f"File contains fewer than {DATA_START_LINE} lines"
        )

    header = rows[HEADER_LINE - 1]
    sampling_rates = rows[SAMPLING_RATE_LINE - 1]

    data = rows[DATA_START_LINE - 1:]

    # Remove completely empty rows
    data = [
        row for row in data
        if any(cell.strip() for cell in row)
    ]

    # The dataset should contain 56 channels
    channel_count = len(header)

    # Convert signal values to floats
    numeric_rows = []

    for row in data:
        try:
            values = [float(x.strip()) if x.strip() else float('nan') for x in row]
            numeric_rows.append(values)
        except ValueError:
            # Ignore malformed rows
            continue

    sample_count = len(numeric_rows)

    # Sampling rates
    rates = []

    for value in sampling_rates:
        value = value.strip()

        match = re.search(r"([0-9.]+)", value)

        if match:
            rates.append(float(match.group(1)))

    # EMG channels occur at positions 1, 8, 15, ...
    emg_rates = rates[0::7]

    # Each sensor has:
    # EMG + ACC X/Y/Z + GYRO X/Y/Z
    imu_rates = []

    for i, rate in enumerate(rates):
        if i % 7 != 0:
            imu_rates.append(rate)

    return {
        "samples": sample_count,
        "channels": channel_count,
        "emg_rates": sorted(set(emg_rates)),
        "imu_rates": sorted(set(imu_rates)),
        "valid_rows": len(numeric_rows),
        "invalid_rows": len(data) - len(numeric_rows),
    }


def main():

    print("=" * 70)
    print("SDALLE DATASET INSPECTION")
    print("=" * 70)

    if not DATASET_DIR.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_DIR}"
        )

    subjects = sorted(
        p for p in DATASET_DIR.glob("Subject_*")
        if p.is_dir()
    )

    print(f"Dataset: {DATASET_DIR}")
    print(f"Subjects found: {len(subjects)}")

    all_trials = []

    for subject_dir in subjects:

        print(f"\n[{subject_dir.name}]")

        activities = sorted(
            p for p in subject_dir.iterdir()
            if p.is_dir()
        )

        for activity_dir in activities:

            csv_files = sorted(
                activity_dir.glob("*.csv")
            )

            print(
                f"  {activity_dir.name:<15}"
                f"{len(csv_files):>3} trials"
            )

            for csv_file in csv_files:

                try:

                    result = parse_trial(csv_file)

                    all_trials.append({
                        "subject": subject_dir.name,
                        "activity": activity_dir.name.capitalize(),
                        "file": csv_file.name,
                        **result
                    })

                except Exception as exc:

                    print(
                        f"    ERROR {csv_file.name}: {exc}"
                    )

    print("\n" + "=" * 70)
    print("DATASET SUMMARY")
    print("=" * 70)

    print(f"Total subjects: {len(subjects)}")
    print(f"Total trials:   {len(all_trials)}")

    activities = sorted(
        set(
            trial["activity"].lower()
            for trial in all_trials
        )
    )

    print(
        "Activities:",
        ", ".join(activities)
    )

    if not all_trials:
        print("No valid trials found.")
        return

    sample_counts = [
        trial["samples"]
        for trial in all_trials
        if trial["samples"] > 0
    ]

    channel_counts = sorted(
        set(
            trial["channels"]
            for trial in all_trials
        )
    )

    emg_rates = sorted(
        set(
            rate
            for trial in all_trials
            for rate in trial["emg_rates"]
        )
    )

    imu_rates = sorted(
        set(
            rate
            for trial in all_trials
            for rate in trial["imu_rates"]
        )
    )

    print("\nSignal structure:")
    print(
        f"  Channels per trial: {channel_counts}"
    )

    print(
        f"  EMG sampling rates: {emg_rates} Hz"
    )

    print(
        f"  IMU sampling rates: {imu_rates} Hz"
    )

    print("\nSamples per trial:")

    print(
        f"  Minimum: {min(sample_counts):,}"
    )

    print(
        f"  Maximum: {max(sample_counts):,}"
    )

    print(
        f"  Mean:    "
        f"{statistics.mean(sample_counts):,.1f}"
    )

    print(
        f"  Median:  "
        f"{statistics.median(sample_counts):,.1f}"
    )

    invalid_rows_total = sum(trial.get("invalid_rows", 0) for trial in all_trials)
    print(
        f"  Invalid rows: {invalid_rows_total:,}"
    )

    print("\nFirst five trials:")

    for trial in all_trials[:5]:

        print(
            f"  {trial['subject']} / "
            f"{trial['activity']} / "
            f"{trial['file']} : "
            f"{trial['samples']:,} samples"
        )

    print("\nInspection complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()

