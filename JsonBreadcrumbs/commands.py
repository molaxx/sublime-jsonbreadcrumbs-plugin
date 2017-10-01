import random
import sys
import os

import sublime
import sublime_plugin

from .utils import jsonbreadcrumbs_parser as parser

from .utils.sublime_utils import RegionStream
from .utils.event_types import SYNTAX_CHANGE, SELECTION_MODIFIED

STATUS_KEY = 'jbc'
SIMPLE_SCOPES = ['constant.numeric.json',
                 'constant.language.json',
                 'string.quoted.double.json']

class CopyJsonBreadcrumbCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if 'JSON' in self.view.settings().get('syntax'):
            sublime.set_clipboard(self.view.get_status(STATUS_KEY))


class JsonWhereCommand(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        events = kwargs['events']
        # for region in self.view.sel()
        if events & (SYNTAX_CHANGE | SELECTION_MODIFIED):
            if not self.is_syntax_json():
                self.view.erase_status(STATUS_KEY)
            else:
                for region in self.view.sel():
                    path = ''
                    if region.begin() != 0:
                        local_scope_region = self.view.extract_scope(region.begin())
                        local_scope_name = self.view.scope_name(region.begin())

                        left_region = sublime.Region(0,region.begin())
                        # print local_scope_region, local_scope_name, left_region
                        if any(simple_scope in local_scope_name for simple_scope in SIMPLE_SCOPES):
                            left_region = left_region.cover(local_scope_region)

                        path = get_jpath_at_end_of_region(self.view, left_region)

                    self.view.set_status(STATUS_KEY,path)
                    break;

    def is_syntax_json(self):
        return 'JSON' in self.view.settings().get('syntax')

def get_jpath_at_end_of_region(view,region):
    region_stream = RegionStream(view, region)
    return parser.get_path(region_stream)


