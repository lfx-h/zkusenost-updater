# Excel-to-SQL Merge Guide for `tagy` and `nadpis` Updates

This guide walks you through updating **only the `tagy` and `nadpis` columns** in an existing SQL Server table (`MainTable`) using a modified Excel file. Unmodified rows in the database will remain untouched.

---

## Prerequisites
- **SQL Server Management Studio (SSMS)** installed.
- **Excel file** with columns:
  - `zkID` (matches existing IDs in `MainTable`)
  - `tagy` (new values to update)
  - `nadpis` (new values to update)
- Permissions to create/update tables in your SQL database.

---

## Step 1: Create a Temporary Staging Table
Run this SQL script to create `TempTable` with matching data types:
```sql
CREATE TABLE TempTable (
    zkID INT PRIMARY KEY,
    tagy NVARCHAR(MAX),
    nadpis NVARCHAR(255)
);
```

---

## Step 2: Import Excel Data into `TempTable`
1. **Open SQL Server Import Wizard**:
   - Right-click your database → **Tasks** → **Import Data**.
   - Choose **Microsoft Excel** as the data source.
   - Select your Excel file and check **"First row has column names"**.

2. **Map Columns Correctly**:
   - Destination: `TempTable`.
   - Ensure column mappings:
     - `zkID` → `INT` (critical! If the wizard maps it as text, cancel and fix Excel formatting).
     - `tagy` → `NVARCHAR(MAX)`
     - `nadpis` → `NVARCHAR(255)`

3. **Execute the Import**:
   - Run the import and verify data in `TempTable`:
     ```sql
     SELECT * FROM TempTable;
     ```

---

## Step 3: Update `MainTable`
Run this SQL script to update **only matching rows**:
```sql
BEGIN TRANSACTION; -- Optional: Start a transaction for safety

UPDATE m
SET 
    m.tagy = t.tagy,
    m.nadpis = t.nadpis
FROM MainTable m
INNER JOIN TempTable t ON m.zkID = t.zkID; -- Updates only existing zkID matches

-- Verify changes before committing:
SELECT m.zkID, m.nadpis AS OldNadpis, t.nadpis AS NewNadpis, m.tagy AS OldTagy, t.tagy AS NewTagy
FROM MainTable m
INNER JOIN TempTable t ON m.zkID = t.zkID;

COMMIT; -- Run ROLLBACK; if issues are found
```

---

## Step 4: Cleanup
Drop the temporary table after verifying the update:
```sql
DROP TABLE IF EXISTS TempTable;
```

---

## Troubleshooting
### Common Errors:
1. **`zkID` Mismatch**:
   - Symptom: "Conversion failed when converting the nvarchar value 'XYZ' to int."
   - Fix: Ensure `zkID` in Excel is numeric and imported as `INT`.

2. **String Truncation**:
   - Symptom: "String or binary data would be truncated in table 'MainTable'."
   - Fix: Shorten `nadpis` values in Excel to ≤255 characters.

3. **Missing Rows**:
   - Symptom: Some Excel rows aren’t updated.
   - Fix: Verify `zkID` exists in both `MainTable` and `TempTable`.

---

## Best Practices
1. **Backup First**: Run `SELECT * INTO MainTable_Backup FROM MainTable;` before updating.
2. **Validate Excel Data**:
   - Remove duplicates in `zkID`.
   - Ensure no trailing spaces in text fields.
3. **Test with a Subset**: Run the process on a copy of your database first.