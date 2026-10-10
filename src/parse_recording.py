import os
import sys
import csv
import math
from datetime import datetime

# Add the parser folder to Python's import path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARSER_DIR = os.path.join(PROJECT_ROOT, "parser")

sys.path.insert(0, PARSER_DIR)

from parser_mmw_demo import parser_one_mmw_demo_output_packet


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

INPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "recordings",
    "radar_003.dat"
)

OUTPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "output",
    "decoded_radar_003.csv"
)


# ---------------------------------------------------------
# MAIN PARSER
# ---------------------------------------------------------

def parse_recording():

    if not os.path.exists(INPUT_FILE):
        print("ERROR: Recording file not found.")
        print(INPUT_FILE)
        return

    file_size = os.path.getsize(INPUT_FILE)

    print("--------------------------------------------")
    print("AWR1843 RADAR DATA PARSER")
    print("--------------------------------------------")
    print("Input file :", INPUT_FILE)
    print("File size  :", file_size, "bytes")
    print()

    # Read complete binary recording
    with open(INPUT_FILE, "rb") as file:
        all_bin_data = file.read()

    total_bytes_parsed = 0
    frame_number = 0

    rows = []

    print("Starting parser...")
    print()

    while total_bytes_parsed < len(all_bin_data):

        remaining_data = all_bin_data[
            total_bytes_parsed:
        ]

        try:

            result = parser_one_mmw_demo_output_packet(
                remaining_data,
                len(remaining_data)
            )

        except TypeError:

            # Some SDK 3.6 parser versions have
            # an optional DEBUG parameter.
            result = parser_one_mmw_demo_output_packet(
                remaining_data,
                len(remaining_data),
                False
            )

        except Exception as error:

            print()
            print("Parser error:")
            print(error)
            print()

            break

        (
            parser_result,
            header_start_index,
            packet_size,
            num_detected_objects,
            num_tlv,
            sub_frame_number,
            detected_x,
            detected_y,
            detected_z,
            detected_velocity,
            detected_range,
            detected_azimuth,
            detected_elevation,
            detected_snr,
            detected_noise
        ) = result

        # ---------------------------------------------
        # Successful frame
        # ---------------------------------------------

        if parser_result == 0:

            frame_number += 1

            print(
                f"Frame {frame_number}: "
                f"{num_detected_objects} objects"
            )

            for object_id in range(num_detected_objects):

                x = float(detected_x[object_id])
                y = float(detected_y[object_id])
                z = float(detected_z[object_id])

                velocity = float(
                    detected_velocity[object_id]
                )

                radar_range = float(
                    detected_range[object_id]
                )

                azimuth = float(
                    detected_azimuth[object_id]
                )

                elevation = float(
                    detected_elevation[object_id]
                )

                snr = float(
                    detected_snr[object_id]
                )

                noise = float(
                    detected_noise[object_id]
                )

                # Calculate range from X/Y/Z
                calculated_range = math.sqrt(
                    x * x +
                    y * y +
                    z * z
                )

                # Store one row
                rows.append(
                    [
                        datetime.now().isoformat(
                            timespec="milliseconds"
                        ),
                        frame_number,
                        object_id,
                        sub_frame_number,
                        x,
                        y,
                        z,
                        radar_range,
                        calculated_range,
                        velocity,
                        azimuth,
                        elevation,
                        snr,
                        noise
                    ]
                )

            # Move to next packet
            total_bytes_parsed += (
                header_start_index +
                packet_size
            )

        else:

            print(
                "WARNING: Parser could not decode "
                "the next frame."
            )

            break

    # -----------------------------------------------------
    # SAVE CSV
    # -----------------------------------------------------

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        newline=""
    ) as csv_file:

        writer = csv.writer(csv_file)

        writer.writerow(
            [
                "timestamp",
                "frame_id",
                "object_id",
                "subframe",
                "x_m",
                "y_m",
                "z_m",
                "range_m",
                "calculated_range_m",
                "velocity_mps",
                "azimuth_deg",
                "elevation_deg",
                "snr_db",
                "noise"
            ]
        )

        writer.writerows(rows)

    print()
    print("--------------------------------------------")
    print("PARSING COMPLETE")
    print("--------------------------------------------")
    print("Frames parsed :", frame_number)
    print("Rows created  :", len(rows))
    print("CSV file      :", OUTPUT_FILE)
    print("--------------------------------------------")


if __name__ == "__main__":
    parse_recording()