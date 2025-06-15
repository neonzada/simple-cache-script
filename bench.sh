#!/bin/bash
#usage: ./bench.sh <config> <[go, li]>

mkdir -p results
rm -f results/*

CONFIG_FILE=$1
BENCHMARK=$2

COMPILER_PATH="benchmarks/$BENCHMARK/${BENCHMARK}.ss"

if [[ "$BENCHMARK" == "go" ]]; then
  INPUT_PATH="benchmarks/go/2stone9.in"
  EXTRA_ARGS="50 9"
elif [[ "$BENCHMARK" == "li" ]]; then
  INPUT_PATH="benchmarks/li/train.lsp"
  EXTRA_ARGS=""
else
  echo "ERROR: undefined benchmark"
  exit 1
fi

count=1

while IFS= read -r config_line; do
  echo "Running config: $config_line"
  CONFIG_ARGS=($config_line)

  COMMAND=(./sim-cache "${CONFIG_ARGS[@]}" "$COMPILER_PATH" $EXTRA_ARGS "$INPUT_PATH")
  echo "Command: ${COMMAND[*]}"

  OUTPUT_FILE="results/${BENCHMARK}_$(echo $config_line | tr ' :/' '_').out"
  "${COMMAND[@]}" 2> "$OUTPUT_FILE" #sim-cache prints to stderr

  SIM_NUM_INSN=$(grep -oP "sim_num_insn\s+(\d+)" "$OUTPUT_FILE" | awk '{print $2}')
  SIM_NUM_REFS=$(grep -oP "sim_num_refs\s+(\d+)" "$OUTPUT_FILE" | awk '{print $2}')

  IL1_MISSES=$(grep -oP "il1\.misses\s+(\d+)" "$OUTPUT_FILE" | awk '{print $2}')
  IL1_HITS=$(grep -oP "il1\.hits\s+(\d+)" "$OUTPUT_FILE" | awk '{print $2}')
  IL1_MISSRATE=$(grep -oP "il1\.miss_rate\s+(-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)" "$OUTPUT_FILE" | awk '{print $2}') #fuckass regex
  
  DL1_MISSES=$(grep -oP "dl1\.misses\s+(\d+)" "$OUTPUT_FILE" | awk '{print $2}')
  DL1_HITS=$(grep -oP "dl1\.hits\s+(\d+)" "$OUTPUT_FILE" | awk '{print $2}')
  DL1_MISSRATE=$(grep -oP "dl1\.miss_rate\s+(-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)" "$OUTPUT_FILE" | awk '{print $2}')

  echo "$(echo "$config_line" | grep -oP "(?<=-cache:il1\s)il1:[^ ]+"),$IL1_MISSRATE,$DL1_MISSRATE" >> results/missrates.csv

  echo "================Benchmark $count================" >> results/results.txt
  echo -e "sim_num_insn=$SIM_NUM_INSN\nsim_num_refs=$SIM_NUM_REFS\n\n" >> results/results.txt
  echo -e "$(echo "$config_line" | grep -oP "(?<=-cache:il1\s)il1:[^ ]+")\nmisses=$IL1_MISSES\nhits=$IL1_HITS\nmissrate=$IL1_MISSRATE\n" >> results/results.txt
  echo -e "$(echo "$config_line" | grep -oP "(?<=-cache:dl1\s)dl1:[^ ]+")\nmisses=$DL1_MISSES\nhits=$DL1_HITS\nmissrate=$DL1_MISSRATE" >> results/results.txt
  echo -e "===========================================\n\n" >> results/results.txt

  count=$((count+1))

done < "$CONFIG_FILE"

python3 plot.py