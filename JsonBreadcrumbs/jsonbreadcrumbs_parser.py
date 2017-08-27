import os
import sys
BASEPATH = os.path.dirname(os.path.realpath(__file__))
sys.path = [BASEPATH, '%s/dist_hack' %BASEPATH] + sys.path
from yajl import YajlContentHandler, YajlParser, YajlError


def get_path(json_stream):
    path_getter = ContentHandler()
    parser = YajlParser(path_getter)
    try:
        parser.parse(f=json_stream)
    except YajlError as e:
        if 'premature EOF' in e.value:
            pass
        else:
            return 'invalid json'
    return path_getter.get_path()


class ContentHandler(YajlContentHandler):
    def __init__(self):
        self.path = ['$']
        self.in_array = False
        self.array_index = 0

    def get_path(self):
        return ''.join(map(str,self.path))
    def parse_start(self):
        ''' Called before each stream is parsed '''
    def parse_buf(self):
        ''' Called when a complete buffer has been parsed from the stream '''
    def complete_parse(self):
        ''' Called when the parsing of the stream has finished '''

    def _check_handle_value_in_array(self):
        if type(self.path[-1]) is Array:
            self.path[-1].next()

    def yajl_null(self, ctx):
       self._check_handle_value_in_array()

    
    def yajl_boolean(self, ctx, boolVal):
        self._check_handle_value_in_array()
    
    def yajl_number(self, ctx, stringNum):
        self._check_handle_value_in_array()
    
    def yajl_string(self, ctx, stringVal):
        self._check_handle_value_in_array()

    def yajl_start_map(self, ctx):
        self._check_handle_value_in_array()

        self.path.append(Map())
        pass
    
    def yajl_map_key(self, ctx, key):
        self.path[-1].current_key(key)

    def yajl_end_map(self, ctx):
        self.path.pop()

    def yajl_start_array(self, ctx):
        self._check_handle_value_in_array()
        self.path.append(Array())
    
    def yajl_end_array(self, ctx):
        self.path.pop()
        
class Map(object):
    def __init__(self):
        self.currKey = ''

    def current_key(self,key):
        self.currKey = "['{0}']".format(key)
    
    def __str__(self):
        return self.currKey

class Array(object):
    def __init__(self):
        self.currIndex = None

    def next(self):
        if self.currIndex == None:
            self.currIndex = 0
        else:
            self.currIndex += 1

    def __str__(self):
        return "[{0}]".format(self.currIndex if self.currIndex != None else 0)




import StringIO

def F(name, excpected, actual):
    return name + " Failed: excpected: {0}, actual: {1}".format(excpected,actual)

def test_case(input, excpected, description):
    json = StringIO.StringIO(input)
    actual = get_path(json)
    assert actual == excpected, F(description, excpected, actual)



def test():
    test_case("","$","before json")
    test_case("{","$","in root")
    test_case("{}", "$", "after json")
    
    test_case('{"a"', "$['a']", "after key defined before :")
    test_case('{"a":', "$['a']", "after key defined after : before value")

    test_case('{"a":3', "$['a']", "after value in map")
    test_case('{"a":3,', "$['a']", "between values in map")
    test_case('{"a":3,"b"',"$['b']", "second key in map")
    test_case('{"a":3,"b":',"$['b']", "jsut before value of second key in map")
    test_case('{"a":3,"b":1,',"$['b']", "value of second key in map")
    test_case('{"a":3,"b":1}',"$", "after map with values")
    test_case('{"a":3,"b":1,"c":"string"',"$['c']", "key with string values")

    test_case('[','$[0]',"in root array, before first value")
    test_case('[1','$[0]',"first num value in array")
    test_case('["','$[0]',"in first string value in array")
    test_case('["kaki"','$[0]',"after first string value in array")
    test_case('["kaki",1','$[1]',"before start second value in array")
    test_case('["kaki",1]','$',"after array")

    test_case('["kaki",1,{}','$[2]',"deep 1")
    test_case('["kaki",1,{','$[2]',"deep 2")
    test_case('["kaki",1,{"k"',"$[2]['k']","deep 3")
    test_case('["kaki",1,{"k":',"$[2]['k']","deep 3")
    test_case('["kaki",1,{"k":[',"$[2]['k'][0]","deep 3")
    test_case('["kaki",1,{"k":[{"hi":[',"$[2]['k'][0]['hi'][0]","deep 3")
    test_case('["kaki",1,{"k":[{"hi":[]',"$[2]['k'][0]['hi']","deep 3")
    test_case('["kaki",1,{"k":[{"hi":["2","3","4"',"$[2]['k'][0]['hi'][2]","deep 3")

    test_case('[[0],[', "$[1][0]", "second member is array after nested array")
    test_case('[[0],[1]', "$[1]", "after second member array after nested array")

    test_case('{"flags":[["archive",1],["data",43]', "$['flags'][1]", "bug")
    print "ALL OK!"
test()



