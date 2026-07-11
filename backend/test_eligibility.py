from services.eligibility import check_eligibility

# OBC undergrad, 3L income -> should match css-college only
# (nmmss needs class9-12, not undergraduate; ishan-uday needs undergraduate but no state given so it'll still show)
profile = {"category": "OBC", "education_level": "undergraduate", "annual_family_income": 300000}
matches = check_eligibility(profile)
print(f"OBC undergrad, 3L income -> {len(matches)} matches:")
for m in matches:
    print(" -", m["name"])

print()

# Class 10 student -> should match nmmss, NOT css-college (wrong level) or ishan-uday (wrong level)
profile2 = {"education_level": "class10", "annual_family_income": 100000}
matches2 = check_eligibility(profile2)
print(f"Class 10, 1L income -> {len(matches2)} matches:")
for m in matches2:
    print(" -", m["name"])