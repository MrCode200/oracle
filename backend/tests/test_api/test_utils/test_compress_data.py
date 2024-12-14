import pandas as pd
import pytest
from src.api.utils import compress_data

INPUT_1 = {
    "Open": [100, 105, 102, 108, 110, 112, 115, 118],
    "High": [105, 108, 110, 112, 115, 120, 125, 130],
    "Low": [95, 102, 100, 106, 108, 110, 114, 117],
    "Close": [104, 107, 108, 110, 113, 119, 123, 128],
    "Dividends": [0, 0, 0, 0, 0, 0, 0, 0],
}

EXPECTED_OUTPUT_1 = {
    "Open": [100, 102, 110, 115],
    "High": [108, 112, 120, 130],
    "Low": [95, 100, 108, 114],
    "Close": [107, 110, 119, 128],
    "Dividends": [0, 0, 0, 0]
}

index_input = pd.date_range(start="2022-01-01", periods=8, freq="D")
index_output = pd.date_range(start="2022-01-01", periods=4, freq="2D")

input_df = pd.DataFrame(INPUT_1, index=index_input, columns=["Open", "High", "Low", "Close", "Dividends"])
expected_output_df = pd.DataFrame(EXPECTED_OUTPUT_1, index=index_output, columns=["Open", "High", "Low", "Close", "Dividends"])


def test_compress_data_with_valid_interval():
    pd.testing.assert_frame_equal(compress_data(input_df, "1d"), input_df)
    pd.testing.assert_frame_equal(compress_data(input_df, "1h"), input_df)



@pytest.mark.parametrize("input_data_frame, output_data_frame", [(input_df, expected_output_df)])
@pytest.mark.parametrize("interval", ["2d"])
def test_compress_data(input_data_frame, output_data_frame, interval):
    compressed_data_frame: pd.DataFrame = compress_data(input_data_frame, interval)
    try:
        pd.testing.assert_frame_equal(compressed_data_frame, output_data_frame)
    except AssertionError as e:
        # Print out the difference between the two DataFrames
        print("\nDataFrames are not equal. Here's the comparison:\n")

        # Compare the indices to see if the index is the issue
        print("Index differences:")
        print("compressed_data_frame:\n", compressed_data_frame.index)
        print("Expected output index:\n", output_data_frame.index)

        # Compare values of both DataFrames
        print("\ncompressed_data_frame:\n", compressed_data_frame)
        print("\nExpected Output DataFrame:\n", output_data_frame)

        raise e