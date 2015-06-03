import importlib.machinery
import sys
import os
import argparse
from subprocess import Popen, PIPE

import bdp.node

class BdpError(Exception):
    pass

def render_tikz(fin, fout=None, outdir=None):
    found = False
    importlib.reload(bdp.node)

    loader = importlib.machinery.SourceFileLoader("", fin)
    import time

    start = time.time()

    bdp_mod = loader.load_module()
    end = time.time()
    print ('Elapsed:' + str(end - start))

    if fout is None:
        fout = os.path.splitext(os.path.basename(fin))[0] + '.tex'

    if outdir is None:
        outdir = os.path.dirname(fout)
        
    if not outdir:
        outdir = os.path.dirname(fin)
        
    if os.path.dirname(fout) == '':
        fout = os.path.join(outdir, fout)

    with open(fout, 'w') as f:
        f.write(str(bdp_mod.fig))

    return fout

def shell(cmdline, input=None, env=None, stderr=PIPE):
    try:
        process = Popen(cmdline, stdin=PIPE, stdout=PIPE, stderr=stderr, env=env)
    except OSError as exc:
        raise BdpError("cannot start executable `%s`: %s"
                             % (' '.join(cmdline), exc))
    output, error = process.communicate(input)
    if process.returncode != 0:
        if not error:
            error = output
        raise BdpError("`%s` exited with an error:\n%s"
                             % (' '.join(cmdline), error))
    return output


def convert_pdf(tex_file):
    from subprocess import call, STDOUT
    call(["pdflatex",
          "-interaction=nonstopmode",
          "-file-line-error",
          '-output-directory', os.path.dirname(tex_file),
          "-halt-on-error", tex_file], stderr=STDOUT)

def pdf2png(pdf_file, resolution=256):

    outdir = os.path.dirname(pdf_file)
    basename = os.path.basename(pdf_file)
    stem = os.path.splitext(basename)[0]

    cmdline = ["pdftoppm",
               '-r', str(resolution),
               '-f', '1', '-l', '1',
               os.path.join(outdir, stem)+'.pdf',
               os.path.join(outdir, stem)]
    shell(cmdline)
    ppmfile = os.path.join(outdir, stem)+'-1.ppm'
    if not os.path.exists(ppmfile):
        raise BdpError("file not found: %s" % ppmfile)

    data = open(ppmfile, 'rb').read()
    cmdline = ['pnmcrop']
    data = shell(cmdline, data)
    line = data.splitlines()[1]
    width, height = [int(chunk) for chunk in line.split()]
    cmdline = ['pnmtopng',
               '-transparent', 'white',
               '-compression', '9']

    data = shell(cmdline, data)

    open(os.path.join(outdir, stem + '.png'), 'wb').write(data)

def render(fin, fout=None, outdir=None, options={}):
    
    if fout is not None:
        fout_tex = os.path.splitext(fout)[0] + '.tex'
    else:
        fout_tex = None
        
    tex_file = render_tikz(fin, fout_tex, outdir)

    convert_pdf(tex_file)

    if 'c' in options:
        if options['r'] is not None:
            pdf2png(os.path.splitext(tex_file)[0] + '.pdf', resolution=options['r'])
        else:
            pdf2png(os.path.splitext(tex_file)[0] + '.pdf')

def main(arv=sys.argv):

    parser = argparse.ArgumentParser(
        description='Block Diagram in Python renderer.'
    )

    parser.add_argument('input', metavar='input',
                        help="Input BDP file")
    
    parser.add_argument('output', metavar='outdir',
                        help="Output file")
    
    parser.add_argument('-d', '--outdir',
                        default = '',
                        help="Output directory")

    parser.add_argument('-c', action='store_true')
    parser.add_argument('-r')

    opts = parser.parse_args(sys.argv[1:])

    options = opts.__dict__
    
    render(opts.input, opts.output, None, options)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
