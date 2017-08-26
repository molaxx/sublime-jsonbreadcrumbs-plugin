import sublime, sublime_plugin

class RegionStream(object):
    def __init__(self, view, region):
        self.view = view
        self.start = region.begin()
        self.end = region.end()

    def read(self, size):
        buf = ''
        to_read = min(self.start + size, self.end)
        requested_region = sublime.Region(self.start, to_read)

        if not requested_region.empty():
            buf = self.view.substr(requested_region)

        self.start = to_read

        return buf

def test():
    class MockView(object):
        def __init__(self, buf):
            self.buf = buf

        def substr(self, region):
            return self.buf[region.begin():region.end()]

    rs = RegionStream(MockView(""), sublime.Region(0,0))
    assert rs.read(100) == '', "read more when empty"

    rs = RegionStream(MockView("a"), sublime.Region(0,1))
    assert rs.read(100) == 'a', "read more when empty"

    rs = RegionStream(MockView("1234567890"), sublime.Region(0,3))
    assert rs.read(2) == '12', "read part 1"
    assert rs.read(1) == '3', "read part 2"
    assert rs.read(1) == '', "read after done"

    print 'ALL OK'

test()