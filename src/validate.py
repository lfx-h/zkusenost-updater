import pandas as pd
import re

def check_df_integrity(original_df: pd.DataFrame, modified_df: pd.DataFrame) -> dict:
    errors = {}

    # 1. Check if the number of rows and columns are the same
    if original_df.shape != modified_df.shape:
        errors["shape_mismatch"] = {
            "original_shape": original_df.shape,
            "modified_shape": modified_df.shape
        }

    # 2. Check if all columns are present and in the same order
    if list(original_df.columns) != list(modified_df.columns):
        errors["column_mismatch"] = {
            "missing_in_modified": list(set(original_df.columns) - set(modified_df.columns)),
            "extra_in_modified": list(set(modified_df.columns) - set(original_df.columns))
        }

    # Helper functions for format validation of modifiable columns:
    def is_valid_tagy(value) -> bool:
        """
        Validates that 'tagy' is a string that is either empty or a comma+space separated list.
        Valid examples: "", "tagb", "tagb, tagc, taga"
        Missing values (NaN) are treated as valid.
        """
        if pd.isna(value):
            return True
        if not isinstance(value, str):
            return False
        if value == "":
            return True
        return True

    def is_valid_nadpis(value) -> bool:
        """
        Validates that 'nadpis' is a string.
        Missing values (NaN) are treated as valid.
        """
        if pd.isna(value):
            return True
        return isinstance(value, str)

    def is_valid_prodid(value) -> bool:
        """
        Validates that 'prodID' is a string that is either empty or a comma+space separated list of integers.
        Valid examples: "", "100", "100, 101, 102"
        Missing values (NaN) are treated as valid.
        """
        if pd.isna(value):
            return True
        if not isinstance(value, str):
            return False
        if value == "":
            return True
        tokens = value.split(", ")
        # Ensure that the delimiter is correctly used (re-join should match original string)
        if ", ".join(tokens) != value:
            return False

        return True

    modifiable_columns = {"tagy", "nadpis", "prodID"}

    # 3. Check if any non-modifiable columns have changed
    for col in original_df.columns:
        if col not in modifiable_columns:
            if not original_df[col].equals(modified_df[col]):
                errors.setdefault("data_mismatch", []).append(col)

    # 4. Validate the format of the modifiable columns in modified_df
    if "tagy" in modified_df.columns:
        for index, value in modified_df["tagy"].items():
            if not is_valid_tagy(value):
                errors.setdefault("tagy_format_error", {})[index] = value

    if "nadpis" in modified_df.columns:
        for index, value in modified_df["nadpis"].items():
            if not is_valid_nadpis(value):
                errors.setdefault("nadpis_format_error", {})[index] = value

    if "prodID" in modified_df.columns:
        for index, value in modified_df["prodID"].items():
            if not is_valid_prodid(value):
                errors.setdefault("prodID_format_error", {})[index] = value

    return errors if errors else {"status": "Integrity check passed"}
