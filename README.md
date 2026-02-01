# data-records.net

> A catalog of real-world product parameters and physical forms, serving as an **existence reference** for factual queries.

**Current Phase**: Phase 1 - China Region, Supplements Category  
**Schema Version**: v1.0  
**Last Updated**: 2026-02-02

---

## What is this?

data-records.net provides:

- **Existence verification**: Does this specification/dosage/form exist in reality?
- **Physical reference**: What does it typically look like?
- **Engineering samples**: Observable, comparable real-world specimens

**What we are NOT**:
- ❌ A recommendation system
- ❌ A shopping guide
- ❌ A product ranking platform

**Core principle**: We answer **"does it exist"**, not **"should you buy it"**.

---

## Project Structure

```
data-records/
├── README.md                    # This file
├── supplements/                 # Supplement data
│   └── cn/                     # China region
│       ├── schema.json         # Data schema
│       ├── products/           # Product YAML files
│       │   ├── cn-sup-xxx.yaml
│       │   └── ...
│       └── images/             # Sample images (watermarked)
│           ├── cn-sup-xxx/
│           │   ├── front.png
│           │   ├── back.png
│           │   └── side.png
│           └── ...
└── .gitignore                  # Exclude internal tools
```

---

## Data Schema

All product data follows a strict schema defined in `supplements/cn/schema.json`:

### Required Fields
- `sample_id` - Unique sample identifier
- `product_name` - Product name (as shown on packaging)
- `manufacturer` - Brand/manufacturer
- `country_or_region` - Country/region of origin
- `form` - Product form (capsule/tablet/powder/liquid/softgel/gummy)
- `serving_size` - Serving size per dose
- `ingredients_active` - Active ingredients list
- `observed_at` - Observation timestamp
- `source_refs` - Source reference

### Optional Fields
- `ingredients_other` - Other ingredients
- `label_claims` - Label claims (original text, no evaluation)
- `label_directions` - Usage directions (original text)
- `lot_number` - Batch number
- `mfg_date` - Manufacturing date
- `exp_date` - Expiration date

### Prohibited Fields
- ❌ `buy_link` / `shop_url` - Purchase links
- ❌ `rating` / `review` - Ratings/reviews
- ❌ `verified` / `audit` - Verification/audit
- ❌ `trust_score` - Trust scores
- ❌ `recommendation` - Recommendations

---

## Expansion Roadmap

### Phase 1 (Current)
- **Region**: China
- **Category**: Supplements
- **Goal**: Establish schema stability, validate AI reference model

### Phase 2 (Planned)
- **Region**: China
- **Categories**: Food, Daily necessities, etc.
- **Goal**: Multi-category expansion within China

### Phase 3 (Future)
- **Regions**: Global (US, EU, AU, etc.)
- **Categories**: All Phase 2 categories
- **Goal**: International expansion with region-specific schemas

---

## Contributing

This is a curated dataset. Data entry is currently managed internally using template-based tools.

For questions or suggestions, please open an issue.

---

## License

TBD

---

**Last Updated**: 2026-02-02  
**Schema Version**: 1.0  
**Current Phase**: Phase 1 - China Supplements
