#!/bin/bash

# Define the file name
filename="out"

# Check if the file exists
if [[ ! -f "$filename" ]]; then
    echo "File not found: $filename"
    exit 1
fi

# Define the threshold (10^15)
threshold=$(echo "10^14" | bc)

# Variable to store mmu.total_latency
mmu_total_latency=""

# Read each line of the file
while IFS= read -r line
do
    # Extract 'a' and 'b' using awk, assuming the format is 'a = b'
    a=$(echo "$line" | awk -F ' = ' '{print $1}')
    b=$(echo "$line" | awk -F ' = ' '{print $2}' | awk -F ',' '{print $1}')

    # Remove any non-numeric characters from 'b' (e.g., if 'b' contains commas)
    b_clean=$(echo "$b" | sed 's/[^0-9.]*//g')

    # Check if 'a' is 'mmu.total_latency' and store its value
    if [[ "$a" == "mmu.total_latency" ]]; then
        mmu_total_latency=$b_clean
    fi

    # Check if 'b' is a valid number and greater than the threshold
    if [[ "$b_clean" =~ ^[0-9]+([.][0-9]+)?$ ]] && [[ $(echo "$b_clean > $threshold" | bc) -eq 1 ]]; then
        # Print 'a' and 'b' in scientific notation
        printf "%s = %e\n" "$a" "$b_clean"
    fi
done < "$filename"

# Print mmu.total_latency at the end if it was found
if [[ -n "$mmu_total_latency" ]]; then
    printf "mmu.total_latency = %e\n" "$mmu_total_latency"
fi
