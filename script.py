import pandas as pd
import asyncio
import os
import time
import logging
import sys
import traceback

from src.utils import setup_logger
from src.llm import agent
from src.matching import find_products_in_review
from src.preprocessing import prepare_product_df

setup_logger()

# File to store the last processed index
PROGRESS_FILE = "progress.txt"
DATA_FILE = "data/zkusenosti.xlsx"
PRODUCT_FILE = "data/products.xlsx"
OUTPUT_FILE = "data/products_updated.xlsx"

# Load last saved index if available
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            try:
                ipos = int(f.read().strip())
                logging.info(f"Continuing from index {ipos}...")
                return ipos
            except ValueError:
                return 0
    return 0  # Default start index

# Save progress **only if the Excel file was successfully written**
def save_progress(ipos, df=None):
    try:
        if df:
            logging.info("Saving the excel file.")
            df.to_excel(OUTPUT_FILE, index=False)
        with open(PROGRESS_FILE, "w") as f:
            f.write(str(ipos))
        logging.info(f"Progress saved successfully at index {ipos}.")
    except Exception as e:
        logging.error(f"Failed to save progress! {e}")

# Main processing function
df = pd.read_excel(DATA_FILE)
df_updated = df.copy()
async def process_data():
    product_df = prepare_product_df(pd.read_excel(PRODUCT_FILE))

    ipos = load_progress()
    last_successful_index = ipos  # Track last successful iteration

    try:
        for index, row in df_updated.iloc[ipos:].iterrows():
            logging.info(f"Progress: {index}/{df_updated.shape[0]}")

            try:
                res = await agent({
                    "zkusenost": row['zkusenost'],
                    "lng": row['lng'],
                    "nadpis": row['nadpis']
                })

                new_prod_ids = find_products_in_review(res['zkusenost'], product_df)['ID'].astype(str).tolist()
                existing_prod_ids = row.get('prodID', "").split(", ") if row.get('prodID') else []
                unique_prod_ids = list(dict.fromkeys(existing_prod_ids + new_prod_ids))

                res['prodID'] = ", ".join(unique_prod_ids)
                df_updated.loc[index, ['prodID', 'nadpis', 'tagy']] = [res['prodID'], res['nadpis'], res['tagy']]
                logging.info(res)

                # Save progress only **after** Excel file was saved
                save_progress(index)

            except Exception as e:
                logging.error(f"Error: {e} - Retrying in 60 seconds...")
                time.sleep(60)  # **Retry instead of continuing**
                continue  # Ensures the loop does not exit

    except KeyboardInterrupt:
        logging.warning("KeyboardInterrupt detected! Saving progress before exiting...")
        save_progress(df_updated, last_successful_index)
        logging.warning("Progress saved. You can restart from the last index.")
        raise  # Ensure the script stops

    except Exception as e:
        logging.error(f"Unhandled error! {e}\n{traceback.format_exc()}")
        save_progress(df_updated, last_successful_index)
        logging.error("Progress saved before unexpected crash.")
        sys.exit(1)  # Ensure script exits after handling error

    # Final save after successful completion
    logging.info("Processing complete! Saving final dataset.")
    save_progress(df_updated, df_updated.shape[0])

# Run the script
if __name__ == "__main__":
    try:
        asyncio.run(process_data())
    except KeyboardInterrupt:
        logging.warning("Script manually stopped.")
    except Exception as e:
        logging.error(f"Unexpected script failure: {e}\n{traceback.format_exc()}")
        sys.exit(1)  # Ensure it exits with an error code
    logging.info("Saving file...")
    df_updated.to_excel(OUTPUT_FILE, index=False)
    input("Press Enter to exit...")
