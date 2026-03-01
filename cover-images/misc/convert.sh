#!/bin/bash

# Quality factors
qualities=(50 60 70 80 90)

for f in *.tif *.tiff; do
    [ -e "$f" ] || continue

    base="${f%.*}"

    echo "Converting $f to grayscale PGM..."
    
    # Convert TIFF -> PGM (8-bit grayscale)
    convert "$f" -colorspace Gray -depth 8 "${base}.pgm"

    for q in "${qualities[@]}"; do
        echo "Creating ${base}_qf${q}.jpg"
        cjpeg -quality $q -optimize -sample 1x1 -outfile "${base}_qf${q}.jpg" "${base}.pgm"
    done

    rm "${base}.pgm"

done

echo "All conversions finished."
