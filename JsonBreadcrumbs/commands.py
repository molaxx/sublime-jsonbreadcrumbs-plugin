import random
import sys
import os

import sublime
import sublime_plugin

import jsonbreadcrumbs_parser as parser
from sublime_utils import RegionStream
from events import SYNTAX_CHANGE, SELECTION_MODIFIED

SIMPLE_SCOPES = ['constant.numeric.json',
                 'constant.language.json',
                 'string.quoted.double.json']

class JsonWhereCommand(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        events = kwargs['events']
        # for region in self.view.sel()
        if events & (SYNTAX_CHANGE | SELECTION_MODIFIED):
            if not self.is_syntax_json():
                self.view.erase_status('xjpath')
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

                    self.view.set_status('xjpath',path)
                    break;

    def is_syntax_json(self):
        return 'JSON' in self.view.settings().get('syntax')

def get_jpath_at_end_of_region(view,region):
    region_stream = RegionStream(view, region)
    return parser.get_path(region_stream)


