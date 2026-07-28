#!/usr/bin/env python3
import argparse, shutil, zipfile, hashlib, yaml
from pathlib import Path

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def add_file(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["chat_native","provider_api"], required=True)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--campaign", required=False)
    ap.add_argument("--module-root", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    module = Path(args.module_root)
    work = Path(args.output).with_suffix("")
    if work.exists(): shutil.rmtree(work)
    work.mkdir(parents=True)

    add_file(Path(args.baseline), work/"playbooks"/Path(args.baseline).name)
    add_file(Path(args.candidate), work/"playbooks"/Path(args.candidate).name)

    if args.mode == "chat_native":
        if not args.campaign:
            raise SystemExit("--campaign required for chat_native")
        add_file(Path(args.campaign), work/"campaign.yaml")
        add_file(module/"prompts/PROMPT_EXECUTE_CHAT_NATIVE_TEST_PACKAGE.md",
                 work/"PROMPT_EXECUTE_IN_TEST_CHAT.md")
        add_file(module/"workflows/BEHAVIORAL_MODE_POLICY.yaml",
                 work/"BEHAVIORAL_MODE_POLICY.yaml")
        core = module/"core"/"chat_native_backend_v1"
        if core.exists():
            shutil.copytree(core, work/"prh_chat_native_backend", dirs_exist_ok=True)
    else:
        (work/"README_START_HERE.md").write_text(
            "Provider API package skeleton. Add provider configuration and never embed credentials.\n",
            encoding="utf-8")
        add_file(module/"workflows/BEHAVIORAL_MODE_POLICY.yaml",
                 work/"BEHAVIORAL_MODE_POLICY.yaml")

    readme = f"""# PRH {args.mode} test package

Baseline: {Path(args.baseline).name}
Candidate: {Path(args.candidate).name}
Baseline SHA-256: {sha(Path(args.baseline))}
Candidate SHA-256: {sha(Path(args.candidate))}
"""
    (work/"README_START_HERE.md").write_text(readme, encoding="utf-8")

    sums=[]
    for p in sorted(work.rglob("*")):
        if p.is_file() and p.name != "SHA256SUMS.txt":
            sums.append(f"{sha(p)}  {p.relative_to(work)}")
    (work/"SHA256SUMS.txt").write_text("\n".join(sums)+"\n", encoding="utf-8")

    out=Path(args.output)
    with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
        for p in sorted(work.rglob("*")):
            if p.is_file(): z.write(p,p.relative_to(work.parent))
    print(out)

if __name__ == "__main__":
    main()
