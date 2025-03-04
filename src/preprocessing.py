import pandas as pd


def prepare_product_df(product_df: pd.DataFrame):
    """
    Precompute several variants of the product name to avoid repeating
    regex/substring operations in the matching loop.
    """
    # Ensure lowercase version.
    product_df["nazev_lower"] = product_df["nazev"].str.lower()
    
    # Variant with trailing " star" removed if it exists.
    product_df["nazev_lower_nostar"] = product_df["nazev_lower"].apply(
        lambda s: s[:-5] if s.endswith(" star") else s
    )
    
    # Variant with digits removed.
    product_df["nazev_lower_nodigits"] = product_df["nazev_lower"].str.replace(r'\d+', '', regex=True)
    
    # Combination: no digits and no " star".
    product_df["nazev_lower_nodigits_nostar"] = product_df["nazev_lower_nostar"].str.replace(r'\d+', '', regex=True)
    
    return product_df


def clean_text(text):
    text = text.replace("_x000D_\n", "")
    text = text.replace("_x000D_", "")

    return text