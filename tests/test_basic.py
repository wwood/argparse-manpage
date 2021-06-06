import unittest
import os.path
import sys
import argparse

sys.path = [os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')]+sys.path
from build_manpages.manpage import Manpage


class Tests(unittest.TestCase):

    def test_backslash_escape(self):
        parser = argparse.ArgumentParser('duh')
        parser.add_argument("--jej", help="c:\\something")
        man = Manpage(parser)
        assert 'c:\\\\something' in str(man).split('\n')
        assert '.SH OPTIONS' in str(man).split('\n')

    def test_argument_groups(self):
        parser1 = argparse.ArgumentParser('duh')
        parser = parser1.add_argument_group('g1')
        parser.add_argument("--jej", help="c:\\something")
        parser2 = parser1.add_argument_group('g2')
        parser2.add_argument("--jej2", help="c:\\something")
        parser2.add_argument("--else", help="c:\\something")
        man = Manpage(parser1)
        self.assertIn('.SH G1', str(man).split('\n'))
        self.assertIn('.SH G2', str(man).split('\n'))
        self.assertNotIn('.SH OPTIONS', str(man).split('\n'))

    def test_delete_underscored_arguments(self):
        parser1 = argparse.ArgumentParser('duh')
        parser1.add_argument('--arg-1','-a','--arg_1',action='store_true',
            help='argument with optional underscore or hyphen')
        parser1.add_argument('--arg-2','-b','--arg_2',
            help='argument with optional underscore or hyphen')
        man = Manpage(parser1)
        self.assertIn('\\fB\\-\\-arg\\-1\\fR, \\fB\\-a\\fR', str(man).split('\n'))
        self.assertNotIn('--arg_1', str(man))
        self.assertIn('\\fB\\-\\-arg\\-2\\fR, \\fB\\-b\\fR \\fI\\,ARG_2\\/\\fR', str(man).split('\n'))
        self.assertNotIn('arg_2', str(man))

    def test_respect_double_newlines(self):
        parser1 = argparse.ArgumentParser('duh')
        parser1.add_argument('--arg-1','-a','--arg_1',action='store_true',
            help='argument with optional underscore or hyphen\n\nthen later another paragraph')
        man = Manpage(parser1)
        self.assertIn('argument with optional underscore or hyphen\n\nthen later another paragraph', str(man))

    def test_author_section(self):
        parser1 = argparse.ArgumentParser('duh')
        parser1.add_argument('--arg-1','-a','--arg_1',action='store_true',
            help='argument with optional underscore or hyphen\n\nthen later another paragraph')
        man = Manpage(parser1, authors=['a1 <yes@no>','a3 and <fdassfd>'])
        with open('blah','w') as f:
            f.write(str(man))
        self.assertIn(('.SH AUTHORS\n.P\n.RS 2\n.nf\n'
            'a1 <yes@no>\n'
            'a3 and <fdassfd>'), str(man))



if __name__ == "__main__":
    unittest.main()
