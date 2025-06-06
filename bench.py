import argparse
import subprocess
import re
import matplotlib.pyplot as plt

def draw_graph(missrate, cacheConfig):
  plt.figure(figsize=(8,5))
  plt.bar(missrate, cacheConfig, color='skyblue')

  plt.tight_layout()
  plt.show()

def parse_output(output):
  matches = []
  matches.append(re.search(r"sim_num_insn\s+(\d+)", output).group(1))
  matches.append(re.search(r"sim_num_refs\s+(\d+)", output).group(1))

  matches.append(re.search(r"il1\.misses\s+(\d+)", output).group(1))
  matches.append(re.search(r"il1\.hits\s+(\d+)", output).group(1))
  matches.append(re.search(r"il1\.miss_rate\s+(-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)", output).group(1)) #fuckass regex

  cacheConfig = re.search(r"-cache:il1\s+(\S+)", output).group(1)

  pretty_print_output(matches)
  draw_graph(matches[4], cacheConfig)

def pretty_print_output(matches):
  print("sim_num_insn = ", matches[0])
  print("sim_num_refs = ", matches[1])
  print("il1.misses = ", matches[2])
  print("il1.hits = ", matches[3])
  print("il1.miss_rate = ", matches[4])
  print("\n\n")


def run_sim(config, compilerPath, optArgs, benchPath):
  config_list = config.split()
  try:
    command = ["./simplesim-3.0/sim-cache"]
    for c in config_list:
      command.append(c)

    command.append(compilerPath)
    if optArgs:
      command.append(optArgs)
    
    command.append(benchPath)
    
    print(' '.join(command))
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    parse_output(result.stderr)
  
  except subprocess.CalledProcessError as e:
    print(f"Error occurred: {e.stderr}")

def main() -> None:
  parser = argparse.ArgumentParser(description="sim-cache benchmarking tool")
  parser.add_argument('--config', required=True, help='Path to config file', metavar="<config file>")
  parser.add_argument('--bench', required=True, help='Which benchmark to run (go, li)', metavar="[go, li]")
  
  args = parser.parse_args()

  print(f"Running benchmark with the following config:")
  print(f"\tConfig: {args.config}")
  print(f"\tBench: {args.bench}\n\n")

  compilerPath = benchPath = "Benchmarks/"
  optArgs = []
  
  if(args.bench == "go"):
    compilerPath += "go/go.ss"
    benchPath += "go/2stone9.in"

    # Optional args for the go benchmark
    optArgs.append("50")
    optArgs.append("9")

  elif(args.bench == "li"):
    compilerPath += "li/li.ss"
    benchPath += "li/train.lsp"

  with open(args.config, "r") as f:
    for line in f:
      run_sim(line.strip(), compilerPath, optArgs, benchPath)

if __name__ == "__main__":
  main()