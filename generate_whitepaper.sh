#!/bin/bash

# Default values
DEFAULT_URL="https://expert.email/classify"
DEFAULT_FILENAME="Phantom_Engaged_Whitepaper_Full.pdf"
OUTPUT_DIR="thoughtpaper"

echo "=========================================="
echo "   Phantom Engaged Whitepaper Generator   "
echo "=========================================="

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# 1. Ask for Tool URL
echo ""
read -p "Enter Tool URL [Press Enter for default: $DEFAULT_URL]: " URL
URL=${URL:-$DEFAULT_URL}

# 2. Ask for Output Filename
echo ""
read -p "Enter Output Filename [Press Enter for default: $DEFAULT_FILENAME]: " FILENAME
FILENAME=${FILENAME:-$DEFAULT_FILENAME}

# Ensure filename ends in .pdf
if [[ "$FILENAME" != *.pdf ]]; then
    FILENAME="${FILENAME}.pdf"
fi

# Construct full output path
OUTPUT="${OUTPUT_DIR}/${FILENAME}"

echo ""
echo "------------------------------------------"
echo "Generating PDF..."
echo "URL:  $URL"
echo "File: $OUTPUT"
echo "------------------------------------------"

# Execute using the virtual environment python
./venv/bin/python3 generate_whitepaper_full.py "$URL" "$OUTPUT"

# Check if successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Success! PDF generated."
    echo ""
    # Try to open the file automatically (Mac/Linux)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "$OUTPUT"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open "$OUTPUT"
    fi
else
    echo ""
    echo "❌ Error generating PDF. Please check the logs above."
fi
