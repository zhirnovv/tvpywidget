import os
import re
from io import open


def glowscript_version():
    """
    Extract the Glowscript version from the javascript in the data directory.
    """

    this_dir = os.path.dirname(os.path.abspath(__file__))
    glowscript_lib = os.path.relpath(this_dir, '../vendor/glow', 'glow.min.js')

    with open(glowscript_lib, 'r', encoding='UTF-8') as f:
        glow_contents = f.read()

    matches = re.search(r'glowscript={version:"(.*?)"}', glow_contents)

    if matches:
        gs_version = matches.group(1)
    else:
        raise RuntimeError("Could not determine glowscript version.")

    return gs_version
