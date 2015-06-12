#  This file is part of bdp.
# 
#  Copyright (C) 2015 Bogdan Vukobratovic
#
#  bdp is free software: you can redistribute it and/or modify 
#  it under the terms of the GNU Lesser General Public License as 
#  published by the Free Software Foundation, either version 2.1 
#  of the License, or (at your option) any later version.
# 
#  bdp is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
# 
#  You should have received a copy of the GNU Lesser General 
#  Public License along with bdp.  If not, see 
#  <http://www.gnu.org/licenses/>.

import importlib.machinery
import sys
import os
import argparse
from subprocess import Popen, PIPE

import bdp.node

class BdpError(Exception):
    pass

clear_extensions_pdf = ['.log', '.tex', '.aux']
clear_extensions_png = clear_extensions_pdf + ['.pdf', '-1.ppm']

def render_tikz(fin):
    found = False
    importlib.reload(bdp.node)

    loader = importlib.machinery.SourceFileLoader("", fin)
    import time

    start = time.time()

    bdp_mod = loader.load_module()
    end = time.time()
    print ('Elapsed:' + str(end - start))
    
    return str(bdp_mod.fig)

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
    
    cmd = ["pdflatex",
          "-interaction=nonstopmode",
          "-file-line-error",
          ]
    
    if os.path.dirname(tex_file):
        cmd += ['-output-directory', os.path.dirname(tex_file)]
        
    cmd += ["-halt-on-error", tex_file] 
    call(cmd, stderr=STDOUT)

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

def render_fig(fig, fout=None, outdir=None, options={}):
    """ Renders the BDP figure to PDF or PNG via Latex
    
        :param fout: Output PDF or PNG file
        :type fout: str
        :param outdir: Output PDF or PNG file
        :type outdir: str
        :param options: Dictionary of additional options: 'c', 'p' and 'r'. Please take a look at command line arguments for additional info.
        :type options: dict
    """
    if fout:
        fout_tex = os.path.splitext(fout)[0] + '.tex'
        fout_ext = os.path.splitext(fout)[1]
    else:
        fout_tex = None
        fout_ext = 'pdf'
        
    if outdir is None:
        outdir = os.path.dirname(fout_tex)
        
    if os.path.dirname(fout_tex) == '':
        fout_tex = os.path.join(outdir, fout_tex)

    with open(fout_tex, 'w') as f:
        f.write(str(fig))

    base_tex = os.path.splitext(fout_tex)[0]
    
    convert_pdf(fout_tex)

    clear_exts_list = clear_extensions_pdf

    try:
        render_png = options['p']
    except KeyError:
        render_png = False
        
    try:
        render_png_res = options['r']
    except KeyError:
        render_png_res = False
        
    if render_png or (fout_ext == 'png'):
        if render_png_res is not None:
            pdf2png(base_tex + '.pdf', resolution=render_png_res)
        else:
            pdf2png(base_tex + '.pdf')
            
        clear_exts_list = clear_extensions_png    
        
    try:
        clear_exts = options['c']
    except KeyError:
        clear_exts = False
        
    if clear_exts:
        for ext in clear_exts_list:
            try:
                os.remove(base_tex + ext)
            except OSError:
                pass
        

def render(fin, fout=None, outdir=None, options={}):
    fig = render_tikz(fin)
    
    if not outdir:
        outdir = os.path.dirname(fin)
    
    if not fout:
        fout = os.path.splitext(os.path.basename(fin))[0] + '.pdf'
        
    render_fig(fig, fout, outdir, options)

def argparser():
    parser = argparse.ArgumentParser(
        description="""Depending on the extension of the output file, BDP will generate either PDF or PNG. If output file is not specified, it will have the same name as the input, and generated extension will depend on the [-p] argument value.         
"""
    )

    parser.add_argument('input', metavar='input',
                        help="Input BDP file")
    
    parser.add_argument('-o', '--output', default = '',
                        help="Output PDF or PNG file")
    
    parser.add_argument('-d', '--outdir',
                        default = '',
                        help="Output directory")

    parser.add_argument('-p', action='store_true', help='Render PNG')
    parser.add_argument('-c', action='store_true', help='Clear intermediate files')
    parser.add_argument('-r', help='Number representing DPI resolution of the generated PNG')

    return parser

def main(arv=sys.argv):

    parser = argparser()
    
    opts = parser.parse_args(sys.argv[1:])

    options = opts.__dict__
    
    render(opts.input, opts.output, None, options)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
