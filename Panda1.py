import pandas as pd

# -------------------------------
# Create a DataFrame
# -------------------------------
data = {
    "Name": ["Aman", "Riya", "Rahul", "Priya", "Karan"],
    "Age": [20, 21, 19, 22, 20],
    "Marks": [85, 92, 78, 88, 67],
    "CGPA": [8.5,6.2,7.8,9.2,5.0],
    "Department": ["CSE", "IT", "CSE", "ECE", "IT"]
}

df = pd.DataFrame(data)

# -------------------------------
# Display Data
# -------------------------------
print("Original DataFrame:")
print(df)

print("\nFirst 5 Rows:")
print(df.head())

print("\nLast 5 Rows:")
print(df.tail())

# -------------------------------
# Shape
# -------------------------------
print("\nShape:")
print(df.shape)

# -------------------------------
# Column Names
# -------------------------------
print("\nColumns:")
print(df.columns)

# -------------------------------
# Information
# -------------------------------
print("\nInfo:")
print(df.info())

# -------------------------------
# Statistics
# -------------------------------
print("\nDescribe:")
print(df.describe())

# -------------------------------
# Select Columns
# -------------------------------
print("\nName Column:")
print(df["Name"])

print("\nName and Marks:")
print(df[["Name", "Marks"]])

# -------------------------------
# Select Rows
# -------------------------------
print("\nFirst Row:")
print(df.iloc[0])

print("\nRows 2 to 4:")
print(df.iloc[1:4])

# -------------------------------
# Filter Data
# -------------------------------
print("\nMarks > 80:")
print(df[df["Marks"] > 80])

print("\nDepartment = CSE:")
print(df[df["Department"] == "CSE"])

# -------------------------------
# Sorting
# -------------------------------
print("\nSort by Marks (Ascending):")
print(df.sort_values("Marks"))

print("\nSort by Marks (Descending):")
print(df.sort_values("Marks", ascending=False))

# -------------------------------
# Add New Column
# -------------------------------
df["Result"] = ["Pass", "Pass", "Pass", "Pass", "Pass"]

print("\nAfter Adding Result Column:")
print(df)

# -------------------------------
# Update Column
# -------------------------------
df["Bonus"] = df["Marks"] + 5

print("\nBonus Marks:")
print(df)

# -------------------------------
# Rename Column
# -------------------------------
df.rename(columns={"Marks": "Score"}, inplace=True)

print("\nAfter Renaming:")
print(df)

# -------------------------------
# Missing Values
# -------------------------------
print("\nMissing Values:")
print(df.isnull().sum())

# -------------------------------
# Unique Values
# -------------------------------
print("\nDepartments:")
print(df["Department"].unique())

# -------------------------------
# Value Counts
# -------------------------------
print("\nDepartment Count:")
print(df["Department"].value_counts())

# -------------------------------
# Mean, Max, Min
# -------------------------------
print("\nAverage Score:")
print(df["Score"].mean())

print("\nHighest Score:")
print(df["Score"].max())

print("\nLowest Score:")
print(df["Score"].min())

# -------------------------------
# Group By
# -------------------------------
print("\nAverage Score by Department:")
print(df.groupby("Department")["Score"].mean())

# -------------------------------
# Save CSV
# -------------------------------
df.to_csv("students.csv", index=False)

print("\nData saved as students.csv")