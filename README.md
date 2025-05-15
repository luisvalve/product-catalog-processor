# 🚗 Amazon Product Merge Tool

A robust, modular Python application for merging and enriching automotive product data for e-commerce platforms. Built for speed, accuracy, and maintainability—perfect for your portfolio!

---

## ✨ Features
- **Modular architecture** for easy maintenance and extension
- **Exact output matching** to legacy scripts (for seamless migration)
- **Advanced vehicle description normalization**
- **Brand abbreviation expansion** using a mapping file
- **Automatic removal of engine/alphanumeric codes** from descriptions
- **Year range and numeric filtering** for clean, accurate output
- **Bullet point splitting** for Amazon-style product listings
- **Rich CLI output** with progress spinners and summary tables
- **Comprehensive logging** for debugging and auditing

---

## 🏗️ Example Modular Directory Structure
```
product_merge_project/
├── data/                  # Input/output files (CSV, Excel, mappings)
├── src/
│   ├── config/
│   │   └── settings.py    # Centralized configuration
│   ├── io/
│   │   ├── file_loader.py # All file reading logic
│   │   └── file_writer.py # All file writing logic
│   ├── processors/
│   │   ├── product_enricher.py      # Product enrichment pipeline
│   │   ├── vehicle_matcher.py       # Vehicle compatibility merging
│   │   └── description_normalizer.py# All description cleaning steps
│   ├── utils/
│   │   ├── data_cleaner.py # Stateless helpers
│   │   └── logger.py       # Logging setup
│   └── main.py             # CLI entrypoint
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 🚀 How It Works
1. **Load product and vehicle data** from CSV/Excel
2. **Merge compatibility info** by part number
3. **Expand brand abbreviations** (e.g., "INFI" → "Infiniti")
4. **Normalize and clean vehicle descriptions**
   - Remove engine/alphanumeric codes (e.g., (K23A1))
   - Remove numeric codes outside year range (e.g., (3980))
   - Format year/model blocks for Amazon
5. **Split bullet points** into separate columns
6. **Output a clean, ready-to-upload CSV**

---

## 🧩 Why Modular?
- **Easy to test** each step in isolation
- **Swap in new logic** (e.g., for a different marketplace) with minimal changes
- **Clear separation** of I/O, processing, and utilities

---

## 📦 Portfolio-Ready
- **Modern Python best practices**
- **Rich terminal UI** (spinners, tables, color)
- **Extensible for new data sources or output formats**

---

## 🛠️ Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run the tool
python src/main.py
```

---

## 👨‍💻 Author
Luis Valve — [GitHub](https://github.com/luisvalve)

---

> **Impress employers and clients with a real-world, production-grade data pipeline!** 