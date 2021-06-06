from argparse import SUPPRESS, HelpFormatter, _SubParsersAction, _HelpAction
from collections import OrderedDict
import re

DEFAULT_ACTION_GROUPS = ('positional arguments','optional arguments')


class Manpage(object):
    def __init__(self, parser, authors=[], raw_format=False):
        self.prog = parser.prog
        self.parser = parser
        if not getattr(parser, '_manpage', None):
            self.parser._manpage = []
        self.authors = authors

        self.formatter = self.parser._get_formatter()
        self.mf = _ManpageFormatter(self.prog, self.formatter if raw_format == False else None)
        self.synopsis = self.parser.format_usage().split(':')[-1].split()
        self.description = self.parser.description

    def format_text(self, text):
        # Wrap by parser formatter and convert to manpage format
        return self.mf.format_text(self.formatter._format_text(text)).strip('\n')


    def __str__(self):
        lines = []

        # Header
        lines.append('.TH {prog} "1" Manual'.format(prog=self.prog))

        # Name
        lines.append('.SH NAME')
        line = self.prog
        if getattr(self.parser, 'man_short_description', None):
            line += " \\- " + self.parser.man_short_description
        lines.append(line)

        # Synopsis
        if self.synopsis:
            lines.append('.SH SYNOPSIS')
            lines.append('.B {}'.format(self.synopsis[0]))
            lines.append(' '.join(self.synopsis[1:]))

        # Description
        if self.description:
            lines.append('.SH DESCRIPTION')
            lines.append(self.format_text(self.description))

        # Global options
        printed_option_header = False
        for action_group in self.parser._action_groups:
            if action_group.title in DEFAULT_ACTION_GROUPS and \
                action_group != self.parser._subparsers:
                entry = self.mf.format_action_group(action_group, self.parser.prog)
                if entry != '':
                    if not printed_option_header:
                        lines.append('.SH OPTIONS')
                        printed_option_header = True
                    lines.append(entry)

        # Subparsers definition
        for action_group in self.parser._action_groups:
            if action_group == self.parser._subparsers:
                lines.append(self.mf.format_action_group(action_group, self.parser.prog))

        # Named argument groups
        for action_group in self.parser._action_groups:
            if action_group.title not in DEFAULT_ACTION_GROUPS and \
                action_group != self.parser._subparsers:
                    lines.append('.SH {}'.format(action_group.title.upper()))
                    lines.append(self.mf.format_action_group(action_group, self.parser.prog))
        # Authors
        if len(self.authors) > 0:
            if len(self.authors) == 1:
                lines.append(".SH AUTHOR")
            else:
                lines.append(".SH AUTHORS")

            # init list
            lines.append(self.mf._init_list())
            for author in self.authors:
                lines.append(author)

        if self.parser.epilog != None:
            lines.append('.SH COMMENTS')
            lines.append(self.format_text(self.parser.epilog))

        # Additional Section
        for section in self.parser._manpage:
            lines.append('.SH {}'.format(section['heading'].upper()))
            lines.append(self.format_text(section['content']))

        return '\n'.join(lines).strip('\n') + '\n'


class _ManpageFormatter(HelpFormatter):
    def __init__(self, prog, old_formatter):
        super(HelpFormatter, self).__init__()
        self._prog = prog
        self.of = old_formatter

    def _markup(self, text):
        if isinstance(text, str) and self.of:
            return text.replace('-', r'\-')
        return text

    def _underline(self, text):
        return r'\fI\,{}\/\fR'.format(text)

    def _bold(self, text):
        if not text.strip().startswith(r'\fB'):
            text = r'\fB{}'.format(text)
        if not text.strip().endswith(r'\fR'):
            text = r'{}\fR'.format(text)
        return text

    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            metavar = self._bold(metavar)
            return metavar

        else:
            parts = []
            args_string = ''

            # if the Optional doesn't take a value, format is:
            #    -s, --long
            #
            # if the Optional is --arg-1, --arg_1, display
            #     --arg-1
            # only.
            if action.nargs == 0:
                all_option_strings = list([o for o in action.option_strings])
                for option_string in action.option_strings:
                    if '_' in option_string and option_string.replace('_','-') in all_option_strings:
                        pass # Ignore as this option is already present with underscore
                    else:
                        parts.append(self._bold(option_string))

            # if the Optional takes a value, format is:
            #    -s, --long ARGS
            #
            # if the Optional is --arg-1 ARGS, --arg_1 ARGS, display
            #     --arg-1 ARGS
            # only.
            else:
                default = self._underline(action.dest.upper())
                args_string = ' '+self._format_args(action, default)
                all_option_strings = list([o for o in action.option_strings])
                for option_string in action.option_strings:
                    if '_' in option_string and option_string.replace('_','-') in all_option_strings:
                        pass # Ignore as this option is already present with underscore
                    else:
                        parts.append('{}'.format(self._bold(option_string)))
            return ', '.join(parts)+args_string


    def _format_parser(self, parser, name):
        lines = []
        lines.append(".SH OPTIONS '{0}'".format(name))
        lines.append(parser.format_usage())

        if parser.description:
            lines.append(self.format_text(parser.description))

        groups = parser._action_groups
        if len(groups):
            for group in groups:
                lines.append(self._format_action_group(group, name))

        return lines


    def _format_action(self, action):
        if '--help' in action.option_strings:
            return ""

        parts = []
        parts.append('.TP')

        action_header = self._format_action_invocation(action)
        parts.append(self._markup(action_header))

        # if there was help for the action, add lines of help text
        if action.help:
            if self.of:
                newline_replacement_regex = re.compile(' *\n\n *')
                newline_replacement_sentinal = '====MAN'
                expanded_help = action.help
                expanded_help = newline_replacement_regex.sub(newline_replacement_sentinal, expanded_help)
                help_text = self.of._format_text(expanded_help).strip('\n').replace(newline_replacement_sentinal,'\n\n')
                parts.append(self.format_text(help_text))
            else:
                parts.append(action.help)

        return parts


    def _format_ag_subcommands(self, actions, prog):
        lines = []

        for action in actions:
            lines.append('.TP')
            lines.append(self._bold(prog) + ' ' + self._underline(action.dest))
            if hasattr(action, 'help'):
                lines.append(action.help)

        return '\n'.join(lines)


    def _format_action_group(self, action_group, prog):
        lines = []

        actions = action_group._group_actions
        for action in actions:
            if action.help == SUPPRESS:
                continue

            if isinstance(action, _SubParsersAction):
                # By default, 'positional arguments' is the title of the
                # subcommand action group.
                if action_group.title != 'positional arguments':
                    lines.append('.SH')
                    lines.append(action_group.title.upper())
                else:
                    lines.append('.SS')
                    lines.append(self._bold('Sub-commands'))
                lines.append(self._format_ag_subcommands(
                        action._choices_actions, prog))

                for name, choice in action.choices.items():
                    lines.extend(self._format_parser(choice, prog + ' ' + name))
                continue

            lines.extend(self._format_action(action))

        return '\n'.join(lines)

    def format_action(self, action):
        return self._format_action(action)

    def format_action_group(self, action_group, prog):
        return self._format_action_group(action_group, prog)

    def format_text(self, text):
        return self._markup(text.strip('\n')\
                   .replace('\\', '\\\\')\
                   .replace('\n', '\n') + '\n')

    def _init_list(self):
        return ".P\n.RS 2\n.nf"
