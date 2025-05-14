# 🚀 Product Catalog Processor

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-1.5%2B-brightgreen)](https://pandas.pydata.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A sleek and efficient Python tool for processing product catalog data with beautiful terminal output. Perfect for managing and transforming e-commerce product information! 🛍️

## ✨ Features

- 📊 Process CSV product catalogs with ease
- 🎯 Smart bullet point parsing and formatting
- 💅 Beautiful terminal output with progress indicators
- 🧪 Comprehensive test coverage
- 🚀 Lightning-fast processing

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/product-catalog-processor.git
cd product-catalog-processor
```

2. Create and activate a virtual environment:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🚀 Usage

1. Place your input CSV file in the `data` directory as `input.csv`
2. Run the processor:
```bash
python main.py
```

### 📝 Input Format

Your input CSV should have the following columns:
- PartNumber
- ASIN
- Title
- URL
- Bullets (pipe-separated bullet points)

Example:
```csv
PartNumber,ASIN,Title,URL,Bullets
178-8276,B0010HGZGU,Product Name,https://example.com,"Point 1 | Point 2 | Point 3"
```

### 📤 Output

The processor will:
- Split bullet points into separate columns
- Clean and format the data
- Generate a new CSV file with processed data
- Show a beautiful progress indicator and summary

## 🧪 Running Tests

```bash
python -m unittest test_processor.py
```

## 📁 Project Structure

```
product_catalog_processor/
├── data/
│   └── input.csv
├── main.py
├── test_processor.py
├── requirements.txt
└── README.md
```

## 🤝 Contributing

Contributions are welcome! Feel free to:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⭐ Show Your Support

Give a ⭐️ if this project helped you! 