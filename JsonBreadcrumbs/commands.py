import random
import sys
import os

import sublime
import sublime_plugin

sys.path.append(os.path.join(os.path.dirname(__file__), "dist"))

import parser
from sublime_utils import RegionStream
from events import SYNTAX_CHANGE, SELECTION_MODIFIED


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
                        local_scope = self.view.extract_scope(region.begin())
                        left_region = sublime.Region(0,region.begin()+1)
                        if left_region.intersects(local_scope):
                            left_region = left_region.cover(local_scope)

                        path = get_jpath_at_end_of_region(self.view, left_region)

                    self.view.set_status('xjpath',path)
                    break;

    def is_syntax_json(self):
        return 'JSON' in self.view.settings().get('syntax')

def get_jpath_at_end_of_region(view,region):
    region_stream = RegionStream(view, region)
    return parser.get_path(region_stream)


