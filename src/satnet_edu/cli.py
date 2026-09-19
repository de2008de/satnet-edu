import argparse
from .trace.io import load

def main():
    p=argparse.ArgumentParser(prog='satnet-edu'); sub=p.add_subparsers(dest='command',required=True)
    v=sub.add_parser('validate',help='Validate a recorded trace'); v.add_argument('trace')
    e=sub.add_parser('export-html',help='Package a trace without simulating'); e.add_argument('trace'); e.add_argument('--output',required=True); e.add_argument('--language',choices=['en','zh'],default='en')
    args=p.parse_args()
    try:
        run=load(args.trace)
        if args.command=='validate': print(f"Valid SatNet Edu trace: {len(run.to_dict()['frames'])} samples")
        else: print(run.export_html(args.output,args.language))
    except (ValueError,OSError) as exc: p.exit(2,f'Error: {exc}\n')

if __name__=='__main__': main()
