# -*- coding: utf-8 -*-

import sys
import os
import hashlib
import logging
import subprocess
from pandocfilters import toJSONFilter, Para, Image, get_caption

# Logging setup
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
stderr_handler = logging.StreamHandler(stream=sys.stderr)
stderr_handler.setLevel(logging.DEBUG)
log.addHandler(stderr_handler)

KNOWN_BLOCKDIAG = ["actdiag", "blockdiag", "nwdiag", "packetdiag", "rackdiag", "seqdiag"]

DEFAULT_OUTPUT_FOLDER = '_diags'

def get_output_dir():
    """
    Return the current output dir, creates it if it does not exist.
    @returns the output dir (str)
    """
    path = os.environ.get('BLOCKDIAG_OUTPUT', DEFAULT_OUTPUT_FOLDER)
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def dbg(**ctx):
    for i, (name, value) in enumerate(ctx.iteritems()):
        sys.stderr.write("%d) %s: %s\n" % (i, name, repr(value)))
    sys.stderr.write("%s\n" % sys.argv)


def dump(contents, suffix):
    """
    Creates a file containing the contents in the desired folder
    @returns the filename
    """
    update = True
    hash = hashlib.md5()
    hash.update(contents)
    filename = os.path.join(get_output_dir(), "%s.%s" % (hash.hexdigest(), suffix))
    if os.path.exists(filename):
        with open(filename) as prev_file_desc:
            previous_contents = prev_file_desc.read()
        if previous_contents == contents:
            update = False
    if update:
        with open(filename, 'w') as file_desc:  # Update!
            file_desc.write(contents)
    else:
        log.debug("%s already updated", filename)
    return filename

def convert_to_svg(diagram_filename):
    base, ext = os.path.splitext(diagram_filename)
    svg_filename = '{}.svg'.format(base)
    if os.path.exists(svg_filename):
        log.warning("%s already exsits", svg_filename)
    command = ext[1:]  # Instead of bassing this as argument, we infer it from extension
    command_with_args = '{command} -T SVG -a -o {svg_filename} {diagram_filename}'.format(
        **locals()
    )
    log.warn("About to run %s", command_with_args)
    subprocess.call(command_with_args.split(' '))
    return svg_filename

def change_ext(original_file, new_ext):
    """Changes extensions
    @returns (new_filename, original_ext)"""
    base, original_ext = os.path.splitext(original_file)
    new_filename = '{}.{}'.format(base, new_ext)
    return new_filename, original_ext

def convert_svg_to_ps(svg_filename):
    ps_filename, _ = change_ext(svg_filename, 'ps')
    command = 'rsvg-convert -b "#fff" -f ps -o {ps_filename} {svg_filename}'.format(**locals())
    subprocess.call(command.split(' '))
    return ps_filename

def convert_svg_to_png(svg_filename):
    png_filename, _ = change_ext(svg_filename, 'png')
    command = 'convert {svg_filename} {png_filename}'.format(**locals())
    subprocess.call(command.split(' '))
    return png_filename

def convert_svg_to_pdf(svg_filename):
    """This is trickier, and depends on the platform"""
    pdf_filename, _ = change_ext(svg_filename, 'pdf')
    try:
        if sys.platform == 'darwin':
            inkscape = '/Applications/Inkscape.app/Contents/Resources/script'
        else:
            inkscape = subprocess.check_output('which inkscape'.split()).strip()
        # -z -f "${from_file}" -A "${to_file}"
        svg_filename = os.path.abspath(svg_filename)
        pdf_filename = os.path.abspath(pdf_filename)
        command = '{inkscape} -z -f {svg_filename} -A {pdf_filename}'.format(**locals())
        subprocess.call(command.split(' '))
    except Exception:
        log.warning("Inkscape failed. Using convert.")
        command = 'convert {svg_filename} {pdf_filename}'.format(**locals())
        log.warn("Cmd: %s", command)
        subprocess.call(command.split(' '))
    return pdf_filename

def blockdiag_conversion(key, value, format_, meta):
    """
    Pandoc filter entry point, called by toJSONFilter
    """
    if key == 'CodeBlock':
        [[ident, classes, keyvals], code] = value
        if not classes:
            return
        tool = classes[0]
        caption, typef, keyvals = get_caption(keyvals)
        if tool in KNOWN_BLOCKDIAG:
            diag = dump(code, tool)
            svg_path = convert_to_svg(diag)
            if format_ == 'html':
                # No further conversion required
                return Para([Image([ident, [], keyvals], caption, [svg_path, typef])])
            elif format_ == 'latex':
                # Convert to PS
                pdf_path = convert_svg_to_pdf(svg_path)
                return Para([Image([ident, [], keyvals], caption, [pdf_path, typef])])
            elif format_ == 'docx':
                # Convert to PS
                png_path = convert_svg_to_png(svg_path)
                return Para([Image([ident, [], keyvals], caption, [png_path, typef])])


    elif key == 'Code':
        dbg(**locals())
        pass    
    elif key == "Image":
        #dbg(**locals())
        pass



if __name__ == '__main__':
    toJSONFilter(blockdiag_conversion)

