# Renderer for the lucas-smi block in README.md (used by update_profile.py)
W = 89
def line(s=""): return "| " + s.ljust(W - 1) + "|"
def row(a, b, c): return "| " + a.ljust(39) + " | " + b.ljust(22) + " | " + c.ljust(20) + " |"
def smi(gpus, procs):
    bar = "+" + "-" * W + "+"
    out = [bar,
           line("LUCAS-SMI 2026.10            Driver Version: Berkeley-28        CUDA Version: caffeine"),
           "|" + "-" * 41 + "+" + "-" * 24 + "+" + "-" * 22 + "|",
           row("GPU  Name", "Role", "Status"),
           "|" + "=" * 41 + "+" + "=" * 24 + "+" + "=" * 22 + "|"]
    for i, (n, r, s) in enumerate(gpus):
        out.append(row(f"{i:>3}  {n}", r, s))
    out += [bar, "", bar, line("Processes:"),
            line(f" {'PR#':<7} {'Type':<6} {'Process name':<44} {'Memory (lines +/-)':>22}"),
            "|" + "=" * W + "|"]
    if not procs:
        out.append(line(" No running processes found"))
    for pid, t, name, mem in procs:
        out.append(line(f" #{pid:<6} {t:<6} {name:<44} {mem:>22}"))
    out.append(bar)
    for l in out: assert len(l) in (0, W + 2), (len(l), l)
    return "\n".join(out)
GPUS = [("NVIDIA DevTech Intern", "C++/CUDA DB operators", "Completed (Sum '26)"),
        ("CSL Laboratories", "Founder", "Running since 6/8/26"),
        ("RTX 4090 (home lab)", "llama.cpp + Ollama", "Online")]
