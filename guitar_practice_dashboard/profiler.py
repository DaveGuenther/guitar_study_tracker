import inspect

# Global variable that turns the profile on or off
use_profiler=True

class Profiler():
    __namespace=None
    __show_line_numbers=None
    __callstack=None
    __call_offset=None

    def __init__(self, namespace='', show_line_numbers=False, call_offset=1):
        """
        This class init method should be called at the beginning of a function.  It will echo out the name of the function to the screen.  When the function goes out of scope this class will echo out that the function has been exited.  Intended for use with Shiny for Python server functions
        
        Parameters

        namespace
            (str): this is the value from session.ns if called within shiny server function

        line_numbers
            (bool): If True, this will add line number fo the parent call information.

        offset
            (int): This is the number of calls we want to offset in the call stack in order to make sure the top level is the function that instantiated this class.        
        """
        self.__namespace=namespace
        self.__show_line_numbers = show_line_numbers
        self.__callstack = inspect.stack()
        self.__call_offset = call_offset
        self.profile_func('in')


    def profile_func(self, direction="in"):    
        """
        This function will echo out the name of the function it was called from as well as the namespace (for use with shiny server and module functions).  It will also show information about the parent call.
        Place a call to this function at the beginning and end of each function you want to track.
        
        Parameters

        namespace
            (str): this is the value from session.ns if called within shiny server function

        direction
            (str): one of ['in','out'].  If 'in', this will show the function name and the calling function.  If 'out' it will just show the function name and namespace.

        line_numbers
            (bool): If True, this will add line number fo the parent call information.
        """
        assert direction in ['in','out'], f'direction attribute must be "in" or "out", but got "{direction}".'
        line_num_text=''
        if self.__show_line_numbers:
            line_number = self.__callstack[self.__call_offset+1][2] # parent's calling line number
            line_code = self.__callstack[self.__call_offset+1][4][0].strip() # parent's calling line of code
            line_num_text= str(" -- line: "+str(line_number)+": "+line_code)
        called_func_name = self.__callstack[self.__call_offset+0][3]
        calling_func_name = self.__callstack[self.__call_offset+1][3]
        if direction=='in':
            print(f"******  namespace: {self.__namespace} -- Entering {called_func_name} <- {calling_func_name} {line_num_text}")
        else:
            print(f"******  namespace: {self.__namespace} -- Leaving {called_func_name}")

    def __del__(self):
        self.profile_func("out")