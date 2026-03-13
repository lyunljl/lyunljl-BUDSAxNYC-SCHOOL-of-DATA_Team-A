# Dataset Data Dictionary

Each row in the dataset represents a **ZIP Code Tabulation Area (ZCTA)**.

---

## Geographic Identifiers

| Column | Description | Metric |
|------|-------------|-------|
| geoid | Census geographic identifier for the ZIP Code Tabulation Area | String identifier |
| name | ZIP code associated with the geographic unit | 5-digit ZIP code |

---

## Rent Variables

| Column | Description | Metric |
|------|-------------|-------|
| median_gross_rent | Median monthly gross rent for renter-occupied housing units | USD per month |
| rent_burden_total_renter_households | Total renter households used for rent burden calculations | Number of households |
| rent_30_to_34_9pct_income | Households spending 30–34.9% of income on rent | Number of households |
| rent_35_to_39_9pct_income | Households spending 35–39.9% of income on rent | Number of households |
| rent_40_to_49_9pct_income | Households spending 40–49.9% of income on rent | Number of households |
| rent_50pct_or_more_income | Households spending 50% or more of income on rent | Number of households |

---

## Income and Population

| Column | Description | Metric |
|------|-------------|-------|
| median_household_income | Median annual household income | USD per year |
| total_population | Total population living in the ZIP code | Number of people |

---

## Housing Supply

| Column | Description | Metric |
|------|-------------|-------|
| housing_units_total | Total number of housing units | Number of housing units |
| occupied_units | Total occupied housing units | Number of housing units |
| vacant_units | Total vacant housing units | Number of housing units |

---

## Housing Tenure

| Column | Description | Metric |
|------|-------------|-------|
| renter_occupied_units | Housing units occupied by renters | Number of housing units |
| owner_occupied_units | Housing units occupied by owners | Number of housing units |

---

## Housing Age (Year Built)

| Column | Description | Metric |
|------|-------------|-------|
| built_2020_or_later | Housing units built in 2020 or later | Number of housing units |
| built_2010_2019 | Housing units built between 2010–2019 | Number of housing units |
| built_2000_2009 | Housing units built between 2000–2009 | Number of housing units |
| built_1990_1999 | Housing units built between 1990–1999 | Number of housing units |
| built_1980_1989 | Housing units built between 1980–1989 | Number of housing units |
| built_1970_1979 | Housing units built between 1970–1979 | Number of housing units |
| built_1960_1969 | Housing units built between 1960–1969 | Number of housing units |
| built_1950_1959 | Housing units built between 1950–1959 | Number of housing units |
| built_1940_1949 | Housing units built between 1940–1949 | Number of housing units |
| built_1939_or_earlier | Housing units built before 1940 | Number of housing units |
