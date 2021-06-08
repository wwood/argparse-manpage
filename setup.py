import os
from os.path import dirname, join
import io
from setuptools import setup

def get_version(relpath):
  """Read version info from a file without importing it"""
  for line in io.open(join(dirname(__file__), relpath), encoding="cp437"):
    if "__version__" in line:
      if '"' in line:
        return line.split('"')[1]
      elif "'" in line:
        return line.split("'")[1]

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_readme():
    with open(os.path.join(ROOT_DIR, 'README.md')) as fh:
        return ''.join(fh.readlines())

setup(
    name='argparse-manpage-birdtools',
    version=get_version('build_manpages/__init__.py'),
    url='https://github.com/wwood/argparse-manpage-birdtools',
    license='Apache 2.0',
    author='Ben Woodcroft, Gabriele Giammatteo, Pavel Raiskup',
    author_email='benjwoodcroft@gmail.com, gabriele.giammatteo@eng.it, praiskup@redhat.com',
    maintainer='Ben Woodcroft',
    maintainer_email='benjwoodcroft@gmail.com',
    packages=['build_manpages'],
    description='Format ROFF documents (manual page format) from python\'s ArgumentParser object.',
    long_description=get_readme(),
    long_description_content_type='text/markdown',
    package_data={'': [
            "build_manpages/*",
                       ]},
    data_files=[(".", ["README.md", "LICENSE"])],
    include_package_data=True,
)
