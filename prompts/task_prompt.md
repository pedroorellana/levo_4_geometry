# specialized levo 4 geometry calculator

The intention of this project is to create a specialized geometry calculator for the Levo 4 mountain bike, how geometry will change due diferent adjust.

# Adjustable options that will affect geometry

- Fork length
    - Evaluate only for 160mm, 170mm, and 180mm
- Horst Pivot (2 options)
- Headset Cup  (3 options)
- shock Extension (2 options,levo 4 non evo only)

- Levo 4 and evo are the same frame and rear triangle, only difference is the shock size and a link that connects the shock to the frame.

# calculations details

Take in consideration some change could affect multiples aspects of the geometry, that are not mentioned in the manual. For example, adjusting the headset cup could affect the head angle, seat angle, and reach.

Consider this when building the calculator, and make sure to include all the geometry changes that could be affected by the adjustments.

# Data
All info is under data folder, you could search on internet for more information if needed, but the main source of information is the data folder.

data/levo4_geometry.csv
data/levo4_geometry_evo.csv
data/adjustable_geo_info.png
data/LEVO_G4_USER_MANUAL_ENGLISH.pdf

# Considerations

- Add also rear whell suspension travel to the analysis.

- Show analysis in a jupyter notebook

- Only do analysis and calculations for levo 4 and evo size S4

# Output

All geometry numbers for diferente configuration, for levo 4 and levo 4 evo. Details of options, do all combination posibles. Only for size s4

levo 4
- Fork length: 160mm, 170mm
- Horst Pivot: Option 1, Option 2
- Headset Cup: Option 1, Option 2, Option 3
- Shock Extension: Option 1, Option 2

levo 4 evo
- Fork length: 170mm, 180mm
- Horst Pivot: Option 1, Option 2
- Headset Cup: Option 1, Option 2, Option 3
