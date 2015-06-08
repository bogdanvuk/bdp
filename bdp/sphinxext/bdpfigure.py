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


from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.parsers.rst.directives.images import Figure
from sphinx.util.osutil import ensuredir
from subprocess import Popen, PIPE
import os, os.path, tempfile, shutil
from bdp.render import render
from hashlib import sha1 as sha
from shutil import copyfile

class BdpFigureDirective(Figure):

    required_arguments = 0
    optional_arguments = 1
    has_content = True

    option_spec = Figure.option_spec.copy()
    option_spec['caption'] = directives.unchanged

    def run(self):

        print('Here!')
        print(self.arguments)
        
        text = '\n'.join(self.content)
        try:
            filename = self.arguments[0]
        except:
            filename = None
        
        self.arguments = ['']
        
        try:
            self.content[0] = self.options['caption']

            while len(self.content) > 1:
                self.content.trim_end(len(self.content) - 1)
        except:
            self.content = None
            
        (figure_node,) = Figure.run(self)
        if isinstance(figure_node, nodes.system_message):
            return [figure_node]
        
        if filename:

            env = self.state.document.settings.env
            rel_filename, filename = env.relfn2path(filename)
            env.note_dependency(rel_filename)
            
            figure_node.bdpfile = filename
        
        else:
            figure_node.bdpcontent = text
            
#             print(filename)
#             print(rel_filename)
#             
# #             env = app.env
# #             docdir = os.path.dirname(env.doc2path(env.docname, base=None))
# # 
# #             if filename.startswith('/'):
# #                 filename = os.path.normpath(filename[1:])
# #             else:
# #                 filename = os.path.normpath(os.path.join(docdir, filename))
# #             
# #             env.note_dependency(filename)
# #             filename = os.path.join(env.srcdir, filename)
# #             except:
# #                 continue
# 
#             
#         self.arguments = ['']
#         text = '\n'.join(self.content)
# 
#         try:
#             self.content[0] = self.options['caption']
# 
#             while len(self.content) > 1:
#                 self.content.trim_end(len(self.content) - 1)
#         except:
#             self.content = None
# 
#         (figure_node,) = Figure.run(self)
#         if isinstance(figure_node, nodes.system_message):
#             return [figure_node]
# 
#         figure_node.bdpcontent = text
#         figure_node.bdpfile = text
        return [figure_node]


class BdpFigureError(Exception):
    pass


class bdpfigure(nodes.General, nodes.Element):
    pass

def out_of_date(original, derived):
    """
    Returns True if derivative is out-of-date wrt original,
    both of which are full file paths.
    """
    return (not os.path.exists(derived) or
            (os.path.exists(original) and
             os.stat(derived).st_mtime < os.stat(original).st_mtime))

def render_bdpfigure(app, filename, options):
    directory = os.path.dirname(filename)
    basename = os.path.basename(filename)
    stem = os.path.splitext(basename)[0]
    
    options = {}
    if app.builder.format == 'html':
        options['p'] = True
        options['r'] = app.env.config.bdp_resolution
        name = stem + '.png'
    else:
        name = stem + '.pdf'
        
    outdir = os.path.join(app.builder.outdir, '_bdpfigure')

    try:
        if (not out_of_date(filename, os.path.join(app.builder.outdir, name))):
            print("Skipping:", filename)
            return name
    except FileNotFoundError:
        pass

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    if not os.path.isfile(filename):
        for bdpdir in app.env.config.bdpfigure_bdpinputs:
            bdpdir = os.path.join(app.env.srcdir, bdpdir)
            filename = os.path.join(bdpdir, basename)
            if os.path.isfile(filename):
                break

    render(filename, os.path.join(outdir, name), outdir, options)
     
    copyfile(os.path.join(outdir, name),
             os.path.join(app.builder.outdir, name))

   

#     environ = os.environ.copy()
#     environ['TEXINPUTS'] = outdir + ':'
#     cmdline = [app.env.config.bdpfigure_pdftex,
#                '-halt-on-error',
#                '-interaction', 'nonstopmode',
#                '-output-directory', outdir,
#                os.path.join(outdir, stem) + '.tex']
#     shell(cmdline, env=environ)
# 
    
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
        if hasattr(fig, 'bdpcontent'):
            text = fig.bdpcontent
            hashid = get_hashid(text)
            fname = 'plot-%s' % (hashid)

            if app.builder.format == 'html':
                fout = os.path.join(app.builder.outdir, fname) + '.png'
            else:
                fout = os.path.join(app.builder.outdir, fname) + '.pdf'

            if os.path.exists(fout):
                image=fig.children[0]
                image['uri'] = os.path.join(fout)
                
                continue

            outdir = os.path.join(app.builder.outdir, '_bdpfigure')
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            
            filename = os.path.join(outdir, fname + '.py')
                       
            with open(filename, 'wb') as f:
                f.write("from bdp import *\n\n".encode())
                f.write(text.encode())
        
        elif hasattr(fig, 'bdpfile'):
            filename = fig.bdpfile
        else:
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
    app.add_config_value('bdp_pdftex', 'pdflatex', 'env')
    app.add_config_value('bdp_pdftoppm', 'pdftoppm', 'env')
    app.add_config_value('bdp_pnmcrop', 'pnmcrop', 'env')
    app.add_config_value('bdp_pnmtopng', 'pnmtopng', 'env')
    app.add_config_value('bdp_bdpinputs', [], 'env')
    app.add_config_value('bdp_resolution', 256, 'env')
    app.connect('doctree-read', render_bdp_images)
    app.add_directive('bdp', BdpFigureDirective)
#     app.add_node(bdpfigure,
#                  latex=(visit_bdpfigure, depart_bdpfigure))
