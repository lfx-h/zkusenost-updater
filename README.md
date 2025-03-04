# zkusenost-updater

## Step 1: Prepare Your SQL Table
```sql
CREATE TABLE MainTable (
    zkID INT PRIMARY KEY, 
    artType NVARCHAR(255), 
    datum NVARCHAR(50), 
    prodID NVARCHAR(50), 
    tagy NVARCHAR(MAX), 
    autor_jmeno NVARCHAR(255), 
    autor_prijmeni NVARCHAR(255), 
    autor_id NVARCHAR(50), 
    autor_telefon NVARCHAR(50), 
    autor_email NVARCHAR(255), 
    nadpis NVARCHAR(255), 
    show_it BIT, 
    lng NVARCHAR(10), 
    zdroj NVARCHAR(255), 
    dotaz NVARCHAR(MAX), 
    zkusenost NVARCHAR(MAX), 
    odmena_castka DECIMAL(10,2), 
    odmena_mena NVARCHAR(50), 
    odmena_pripsana BIT, 
    odmenu_pripsal NVARCHAR(255), 
    je_preklad BIT, 
    original_ID INT
);
```

## Step 2: Open SQL Server Import Wizard
1. Open SQL Server Management Studio (SSMS).
2. Connect to your SQL Server instance.
3. Right-click on your database (e.g., YourDatabase).
4. Select Tasks → Import Data.

## Step 3: Select Data Source
1. In the Choose a Data Source window:
    - Select Microsoft Excel as the data source.
    - Click Browse and select your Excel file.
    - Check the box First row has column names.
    - Click Next.
2. In the Choose a Destination window:
    - Select SQL Server Native Client as the destination.
    - Choose your Server name.
    - Select your database.
    - Click Next.

## Step 4: Specify Table Copy or Query
1. Choose Copy data from one or more tables.
2. Click Next.

## **Step 5: Select Source Tables**
1. In the **Select Source Tables and Views** window:
   - Choose the **Excel sheet** (e.g., `Sheet1$`).
   - Set the **destination table** to a new table called `TempTable` (you will create it dynamically).
   - Click **Edit Mappings**.

2. **Edit Mappings**:
   - Ensure all columns from Excel **match** the SQL table structure.
   - Set data types to **NVARCHAR(MAX)** for long text fields.
   - Click **OK**.
   - Click **Next**.

## **Step 6: Execute the Import**
1. Select **Run immediately**.
2. Click **Next** → **Finish**.
3. Wait for the import to complete.

## **Step 7: Update Your Main Table**
Now that the data is in `TempTable`, run this SQL script to update `MainTable`:

```sql
UPDATE m
SET 
    m.artType = t.artType,
    m.datum = t.datum,
    m.prodID = t.prodID,
    m.tagy = t.tagy,
    m.autor_jmeno = t.autor_jmeno,
    m.autor_prijmeni = t.autor_prijmeni,
    m.autor_id = t.autor_id,
    m.autor_telefon = t.autor_telefon,
    m.autor_email = t.autor_email,
    m.nadpis = t.nadpis,
    m.show_it = t.show_it,
    m.lng = t.lng,
    m.zdroj = t.zdroj,
    m.dotaz = t.dotaz,
    m.zkusenost = t.zkusenost,
    m.odmena_castka = t.odmena_castka,
    m.odmena_mena = t.odmena_mena,
    m.odmena_pripsana = t.odmena_pripsana,
    m.odmenu_pripsal = t.odmenu_pripsal,
    m.je_preklad = t.je_preklad,
    m.original_ID = t.original_ID
FROM MainTable m
JOIN TempTable t ON m.zkID = t.zkID;
```

## Step 8: Verify the Update
Once you confirm everything is correct, delete the temporary table:
```sql
DROP TABLE TempTable;
```