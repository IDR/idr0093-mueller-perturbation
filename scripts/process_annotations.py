import sys
import pandas

if len(sys.argv) != 2:
  print("Usage: python process_annotations.py /path/to/annotations.csv")
  exit(1)

in_file = sys.argv[1]
out_file = in_file.replace(".csv", "_mod.csv")

names = ["siRNA Pool Identifier", "Transcript Identifier",
         "Sense Sequence", "Antisense Sequence"]


def split_info(name, row, row_index, df):
  """
  Split a csv entry in column "A 1" with contents separated by ;
  into separate columns "A 1", "A 2", etc. with one item each.
  The respective columns must exist.
  :param name: The row header (without index), "A"
  :param row: The row
  :param row_index: The row index (line number)
  :param df: The dataframe
  :return: None
  """
  try:
    src = f"{name} 1"
    parts = row[src].split(";")
    for i, part in enumerate(parts):
      tgt = f"{name} {i+1}"
      df.at[row_index, tgt] = part
  except:
    pass


df = pandas.read_csv(in_file, dtype=str)
n_rows = len(df)

# create new column for comment
df.insert(10, "Comment [siRNA Pool]", [""] * n_rows)


for ri, row in df.iterrows():
  print(f"{ri+1}/{n_rows}")

  # fix plate names
  plate_name = str(row["Plate"]).strip()
  plate_name = plate_name.zfill(3)
  df.at[ri, "Plate"] = plate_name

  # fix well names
  well_name = str(row["Well"]).strip()
  well_col = well_name[0]
  well_row = int(well_name[1:])
  df.at[ri, "Well"] = well_col+str(well_row)

  # fix GO terms
  if row["Phenotype Term Accession"]:
    rep = str(row["Phenotype Term Accession"]).replace(":", "_")
    df.at[ri, "Phenotype Term Accession"] = rep

  # remove the 'scrambled' comment from gene symbol
  # together with the remarks in siRNA id into comment
  # column
  if row["Gene Symbol"] == "Scrambled":
    tmp = row["siRNA Pool Identifier 1"]
    comment = f"Scrambled, {tmp}"
    df.at[ri, "Comment [siRNA Pool]"] = comment
    df.at[ri, "siRNA Pool Identifier 1"] = ""
    df.at[ri, "Gene Symbol"] = ""
  else:
    # split the three information pieces of these
    # columns into three separate columns
    for name in names:
      split_info(name, row, ri, df)

  # remove all nans
  for ci, cell in enumerate(row):
    if str(cell).lower().strip() == "nan":
      df.iat[ri, ci] = ""


df.to_csv(out_file, index=False)
