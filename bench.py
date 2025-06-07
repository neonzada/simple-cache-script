import argparse
import subprocess
import re
import matplotlib.pyplot as plt
import numpy as np

i_missrate = []
d_missrate = []
cacheConfig = []

def draw_graph() -> None:
  width = 0.35
  
  bar1 = np.arange(len(cacheConfig))
  bar2 = [i+width for i in bar1]
  
  plt.figure(figsize=(10,6))
  plt.bar(bar1, i_missrate, width, label='IL1 Miss Rate', color='skyblue')
  plt.bar(bar2, d_missrate, width, label='DL1 Miss Rate', color='red')

  plt.xlabel("Cache Configuration")
  plt.ylabel("Miss Rate")
  plt.title("L1 Cache Miss Rate per Configuration")
  plt.xticks((bar1+bar2)/2, cacheConfig, ha="center")
  plt.legend()

  plt.ylim(0, 1)
  plt.tight_layout()
  plt.savefig("results.png", dpi=150)


def parse_print_output(output) -> None:
  print("sim_num_insn = ", re.search(r"sim_num_insn\s+(\d+)", output).group(1))
  print("sim_num_refs = ", re.search(r"sim_num_refs\s+(\d+)", output).group(1))

  print("il1.misses = ", re.search(r"il1\.misses\s+(\d+)", output).group(1))
  print("il1.hits = ", re.search(r"il1\.hits\s+(\d+)", output).group(1))
  imiss = re.search(r"il1\.miss_rate\s+(-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)", output).group(1) #fuckass regex
  i_missrate.append(float(imiss))
  print("il1.miss_rate = ", imiss)

  print("dl1.misses = ", re.search(r"dl1\.misses\s+(\d+)", output).group(1))
  print("dl1.hits = ", re.search(r"dl1\.hits\s+(\d+)", output).group(1))
  dmiss = re.search(r"dl1\.miss_rate\s+(-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)", output).group(1)
  d_missrate.append(float(dmiss))
  print("dl1.miss_rate = ", dmiss)
  
  cacheConfig.append(re.search(r"-cache:il1\s+(\S+)", output).group(1))


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
    parse_print_output(result.stderr)
  
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
  optArgs = ""
  
  if(args.bench == "go"):
    compilerPath += "go/go.ss"
    benchPath += "go/2stone9.in"

    # Optional args for the go benchmark
    optArgs += "50 9"

  elif(args.bench == "li"):
    compilerPath += "li/li.ss"
    benchPath += "li/train.lsp"

  with open(args.config, "r") as f:
    for line in f:
      run_sim(line.strip(), compilerPath, optArgs, benchPath)
    
  draw_graph()


if __name__ == "__main__":
  main()