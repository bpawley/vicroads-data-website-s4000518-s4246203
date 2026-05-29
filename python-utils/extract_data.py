import sqlite3, json

conn = sqlite3.connect("database/Road_Accidents.db")
c = conn.cursor()

# ── Level 1A data ──────────────────────────────────────────────────────────────
c.execute("SELECT COUNT(*) FROM Accident")
total_accidents = c.fetchone()[0]

# Wet road accidents (surface condition 2 = Wet)
c.execute("""
    SELECT COUNT(DISTINCT s.ACCIDENT_NO)
    FROM Surface_Cond_Seq s
    JOIN Road_Surface_Cond r ON s.SURFACE_COND = r.SURFACE_COND
    WHERE LOWER(r.SURFACE_COND_DESC) = 'wet'
""")
wet_accidents = c.fetchone()[0]
wet_road_pct = round(wet_accidents / total_accidents * 100, 1)

# Most common atmospheric condition
c.execute("""
    SELECT a.ATMOSPH_COND_DESC, COUNT(*) as cnt
    FROM Atmospheric_Cond_Seq s
    JOIN Amospheric_Cond a ON s.ATMOSPH_COND = a.ATMOSPH_COND
    GROUP BY a.ATMOSPH_COND_DESC
    ORDER BY cnt DESC
    LIMIT 1
""")
row = c.fetchone()
top_atmosph = row[0]

# Night time accidents (light condition IDs for night: check the table)
c.execute("SELECT COND_ID, COND_NAME FROM Light_Condition")
light_conditions = c.fetchall()
print("Light conditions:", light_conditions)

night_ids = [
    lc[0]
    for lc in light_conditions
    if "dark" in lc[1].lower() or "night" in lc[1].lower()
]
print("Night IDs:", night_ids)

if night_ids:
    placeholders = ",".join("?" * len(night_ids))
    c.execute(
        f"SELECT COUNT(*) FROM Accident WHERE LIGHT_CONDITION IN ({placeholders})",
        night_ids,
    )
    night_accidents = c.fetchone()[0]
else:
    night_accidents = 0
night_pct = round(night_accidents / total_accidents * 100, 1)

print(f"\n=== Level 1A Data ===")
print(f"total_accidents: {total_accidents:,}")
print(f"wet_road_pct: {wet_road_pct}%")
print(f"top_atmosph: {top_atmosph}")
print(f"night_pct: {night_pct}%")

# ── Level 2A data ──────────────────────────────────────────────────────────────
# Road surface conditions breakdown
c.execute("""
    SELECT r.SURFACE_COND_DESC, COUNT(DISTINCT s.ACCIDENT_NO) as cnt
    FROM Surface_Cond_Seq s
    JOIN Road_Surface_Cond r ON s.SURFACE_COND = r.SURFACE_COND
    GROUP BY r.SURFACE_COND_DESC
    ORDER BY cnt DESC
""")
surface_data = c.fetchall()
print(f"\n=== Surface Conditions ===")
for row in surface_data:
    print(f"  {row[0]}: {row[1]:,} ({round(row[1]/total_accidents*100,1)}%)")

# Atmospheric conditions breakdown
c.execute("""
    SELECT a.ATMOSPH_COND_DESC, COUNT(DISTINCT s.ACCIDENT_NO) as cnt
    FROM Atmospheric_Cond_Seq s
    JOIN Amospheric_Cond a ON s.ATMOSPH_COND = a.ATMOSPH_COND
    GROUP BY a.ATMOSPH_COND_DESC
    ORDER BY cnt DESC
""")
atmos_data = c.fetchall()
print(f"\n=== Atmospheric Conditions ===")
for row in atmos_data:
    print(f"  {row[0]}: {row[1]:,} ({round(row[1]/total_accidents*100,1)}%)")

# Light conditions breakdown
c.execute("""
    SELECT lc.COND_NAME, COUNT(*) as cnt
    FROM Accident a
    JOIN Light_Condition lc ON a.LIGHT_CONDITION = lc.COND_ID
    GROUP BY lc.COND_NAME
    ORDER BY cnt DESC
""")
light_data = c.fetchall()
print(f"\n=== Light Conditions ===")
for row in light_data:
    print(f"  {row[0]}: {row[1]:,} ({round(row[1]/total_accidents*100,1)}%)")

# Severity ratings per surface condition (avg injury level)
c.execute("""
    SELECT r.SURFACE_COND_DESC,
           COUNT(DISTINCT s.ACCIDENT_NO) as cnt,
           ROUND(AVG(p.INJ_LEVEL), 2) as avg_severity
    FROM Surface_Cond_Seq s
    JOIN Road_Surface_Cond r ON s.SURFACE_COND = r.SURFACE_COND
    JOIN Person p ON s.ACCIDENT_NO = p.ACCIDENT_NO
    GROUP BY r.SURFACE_COND_DESC
    ORDER BY cnt DESC
""")
surface_severity = c.fetchall()
print(f"\n=== Surface with Severity ===")
for row in surface_severity:
    print(f"  {row[0]}: {row[1]:,} accidents, avg severity {row[2]}")

# ── Level 3A data ──────────────────────────────────────────────────────────────
# Average accidents per atmospheric condition
c.execute("""
    SELECT COUNT(DISTINCT s.ACCIDENT_NO) * 1.0 / COUNT(DISTINCT a.ATMOSPH_COND) as avg_per_cond
    FROM Atmospheric_Cond_Seq s
    JOIN Amospheric_Cond a ON s.ATMOSPH_COND = a.ATMOSPH_COND
""")
avg_accidents = round(c.fetchone()[0], 0)

# Conditions above average
c.execute("""
    SELECT a.ATMOSPH_COND_DESC, COUNT(DISTINCT s.ACCIDENT_NO) as cnt
    FROM Atmospheric_Cond_Seq s
    JOIN Amospheric_Cond a ON s.ATMOSPH_COND = a.ATMOSPH_COND
    GROUP BY a.ATMOSPH_COND_DESC
    ORDER BY cnt DESC
""")
all_atmos = c.fetchall()

# compute real average
avg_val = sum(r[1] for r in all_atmos) / len(all_atmos)
print(f"\n=== Level 3A Data ===")
print(f"Average accidents per atmospheric condition: {avg_val:.0f}")
print("\nAll conditions vs average:")
for row in all_atmos:
    diff = row[1] - avg_val
    pct_above = round(diff / avg_val * 100, 1)
    marker = "ABOVE" if diff > 0 else "below"
    print(f"  {row[0]}: {row[1]:,} ({marker} avg by {abs(pct_above)}%)")

conn.close()
