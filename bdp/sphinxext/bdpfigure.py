#
# Copyright (c) 2013, Prometheus Research, LLC
#


from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.parsers.rst.directives.images import Figure
from sphinx.util.osutil import ensuredir
from subprocess import Popen, PIPE
import os, os.path, tempfile, shutil
from bdp.render import render_tikz
from hashlib import sha1 as sha
from shutil import copyfile

class BdpFigureDirective(Figure):

    required_arguments = 0
    has_content = True

    option_spec = Figure.option_spec.copy()
    option_spec['caption'] = directives.unchanged

    def run(self):

        self.arguments = ['']
        text = '\n'.join(self.content)
        
        try:
            self.content[0] = self.options['caption']
            
            while len(self.content) > 1:
                self.content.trim_end(len(self.content) - 1)
        except:
            self.content = None
        
        (figure_node,) = Figure.run(self)
        if isinstance(figure_node, nodes.system_message):
            return [figure_node]

        figure_node.bdpfigure = text
        return [figure_node]


class BdpFigureError(Exception):
    pass


class bdpfigure(nodes.General, nodes.Element):
    pass


def render_bdpfigure(app, filename, options):
    directory = os.path.dirname(filename)
    basename = os.path.basename(filename)
    stem = os.path.splitext(basename)[0]
    name = stem + '.pdf'
    outdir = os.path.join(app.builder.outdir, '_bdpfigure')
    
    try:
        print(os.path.getmtime(filename))
        print(os.path.getmtime(os.path.join(app.builder.outdir, name)))
        if (os.path.getmtime(filename) < 
            os.path.getmtime(os.path.join(app.builder.outdir, name))):
            print("Skipping:", filename)
            return name
    except FileNotFoundError:
        pass

    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    bdpinputs = [directory]
    for bdpdir in app.env.config.bdpfigure_bdpinputs:
        bdpdir = os.path.join(app.env.srcdir, bdpdir)
        bdpinputs.append(bdpdir)
#        bdpinputs.append('')
#         bdpinputs = ':'.join(bdpinputs)
    environ = os.environ.copy()
    environ['TEXINPUTS'] = outdir + ':'
    render_tikz(basename, outdir, bdpinputs)
    cmdline = [app.env.config.bdpfigure_pdftex,
               '-halt-on-error',
               '-interaction', 'nonstopmode',
               '-output-directory', outdir,
               os.path.join(outdir, stem) + '.tex']
    shell(cmdline, env=environ)
    
    copyfile(os.path.join(outdir, stem) + '.pdf', 
             os.path.join(app.builder.outdir, name))
    
#     cmdline = [app.env.config.bdpfigure_pdftoppm,
#                '-r', str(app.env.config.bdpfigure_resolution),
#                '-f', '1', '-l', '1',
#                os.path.join(outdir, stem)+'.pdf',
#                os.path.join(outdir, stem)]
#     shell(cmdline)
#     ppmfile = os.path.join(outdir, stem)+'-1.ppm'
#     if not os.path.exists(ppmfile):
#         raise BdpFigureError("file not found: %s" % ppmfile)
#     
#     data = open(ppmfile, 'rb').read()
#     cmdline = [app.env.config.bdpfigure_pnmcrop]
#     data = shell(cmdline, data)
#     line = data.splitlines()[1]
#     width, height = [int(chunk) for chunk in line.split()]
#     cmdline = [app.env.config.bdpfigure_pnmtopng,
#                '-transparent', 'white',
#                '-compression', '9']
#     
#     data = shell(cmdline, data)
#     
#     open(os.path.join(app.builder.outdir, name), 'wb').write(data)

    return name


def shell(cmdline, input=None, env=None):
    try:
        process = Popen(cmdline, stdin=PIPE, stdout=PIPE, stderr=PIPE, env=env)
    except OSError as exc:
        raise BdpFigureError("cannot start executable `%s`: %s"
                             % (' '.join(cmdline), exc))
    output, error = process.communicate(input)
    if process.returncode != 0:
        if not error:
            error = output
        raise BdpFigureError("`%s` exited with an error:\n%s"
                             % (' '.join(cmdline), error))
    return output


def visit_bdpfigure(self, node):
    pass

def depart_bdpfigure(self, node):
    pass

def get_hashid(text):
    hashkey = text.encode('utf-8')
    hashid = sha(hashkey).hexdigest()
    return hashid

def render_bdp_images(app, doctree):
    for fig in doctree.traverse(nodes.figure):
        if hasattr(fig, 'bdpfigure'):
            text = fig.bdpfigure
            hashid = get_hashid(text)
            fname = 'plot-%s' % (hashid)
            
            if os.path.exists(os.path.join(app.builder.outdir, fname) + '.pdf'):
                continue
            
            outdir = os.path.join(app.builder.outdir, '_bdpfigure')
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            
            filename = os.path.join(outdir, fname + '.py')
            with open(filename, 'wb') as f:
                f.write("from bdp.node import *\n\n".encode())
                f.write(text.encode())
        else:
            try:
                image=fig.children[0]
                filename = image['uri']
                
                basename = os.path.basename(filename)
                extension = os.path.splitext(basename)[1]
                
                if (extension != '.py'):
                    continue
            
                env = app.env
                docdir = os.path.dirname(env.doc2path(env.docname, base=None))
                
                if filename.startswith('/'):
                    filename = os.path.normpath(filename[1:])
                else:
                    filename = os.path.normpath(os.path.join(docdir, filename))
                env.note_dependency(filename)
                filename = os.path.join(env.srcdir, filename)
            except:
                continue

#         try:
        print(filename)
        fname = render_bdpfigure(app, filename, fig)
        print(fname)
        image=fig.children[0]
        image['uri'] = fname
#         except BdpFigureError as exc:
#             app.builder.warn('gnuplot error: ' + str(exc))
#             fig.replace_self(nodes.literal_block(text, text))
#             continue


def setup(app):
    app.add_config_value('bdpfigure_pdftex', 'pdflatex', 'env')
    app.add_config_value('bdpfigure_pdftoppm', 'pdftoppm', 'env')
    app.add_config_value('bdpfigure_pnmcrop', 'pnmcrop', 'env')
    app.add_config_value('bdpfigure_pnmtopng', 'pnmtopng', 'env')
    app.add_config_value('bdpfigure_bdpinputs', [], 'env')
    app.add_config_value('bdpfigure_resolution', 256, 'env')
    app.connect('doctree-read', render_bdp_images)
    app.add_directive('bdpfigure', BdpFigureDirective)
#     app.add_node(bdpfigure,
#                  latex=(visit_bdpfigure, depart_bdpfigure))