import importlib.machinery
import sys
import os
import argparse
from subprocess import Popen, PIPE

import bdp.node

class BdpError(Exception):
    pass

def render_tikz(file_name, bdp_gen_path, search_paths=[]):
    found = False
    importlib.reload(bdp.node)
    try:
        bdp_file_name = file_name
        print(bdp_file_name)
        loader = importlib.machinery.SourceFileLoader("", bdp_file_name)
        bdp_mod = loader.load_module()
        found = True
    except FileNotFoundError:

        print(search_paths)

        if isinstance(search_paths, str):
            bdp_file_name = os.path.join(search_paths, file_name)
            loader = importlib.machinery.SourceFileLoader("", bdp_file_name)
            bdp_mod = loader.load_module()
        else:
            for s in search_paths:
                try:
                    bdp_file_name = os.path.join(s, file_name)
                    print(bdp_file_name)
                    loader = importlib.machinery.SourceFileLoader("tmp", bdp_file_name)
                    bdp_mod = loader.load_module("tmp")
                    found = True
                    break
                except FileNotFoundError as e:
                    print(e)
                    pass

    if not found:
        return

    tex_name = os.path.splitext(os.path.basename(bdp_file_name))[0] + '.tex'

    # bdp_file_name = "/home/personal/doktorat/prj/eclipse_wspace/bdp_test/test"

    # bdp_file_name = "dt_memory_arch"

    # bdp_mod = importlib.import_module(bdp_file_name)


    tikz_prolog = r"""
    \documentclass{standalone}

    \usepackage{tikz}
    \usetikzlibrary{shapes,arrows,decorations.pathreplacing}

    \begin{document}
    \pagestyle{empty}
    \begin{tikzpicture}[yscale=-1, every node/.style={inner sep=0,outer sep=0, anchor=center}]

    """

    tikz_epilog = r"""
    \end{tikzpicture}


    \end{document}
    """

#     os.chdir(bdp_gen_path)
    print(bdp_gen_path)
    if not os.path.exists(bdp_gen_path):
        print("Does not exist!")

    tex_file = os.path.join(bdp_gen_path, tex_name)
    with open(tex_file, 'w') as f:
        f.write(tikz_prolog)

        for obj in bdp_mod.obj_list:
            f.write(obj)
    #         f.write(obj.render_tikz())

        f.write(tikz_epilog)

    return tex_file

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


def main(arv=sys.argv):

    parser = argparse.ArgumentParser(
        description='Block Diagram in Python renderer.'
    )

    parser.add_argument('input', metavar='input',
                        help="Input BDP file")
    parser.add_argument('outdir', metavar='outdir',
                        help="Output directory")

    parser.add_argument('-c', action='store_true')
    parser.add_argument('-r')

    opts = parser.parse_args(sys.argv[1:])

    tex_file = render_tikz(opts.input, opts.outdir)

    convert_pdf(tex_file)
    
    if opts.c:
        if opts.r is not None:
            pdf2png(os.path.splitext(tex_file)[0] + '.pdf', resolution=opts.r)
        else:
            pdf2png(os.path.splitext(tex_file)[0] + '.pdf')

if __name__ == '__main__':
    sys.exit(main(sys.argv))
