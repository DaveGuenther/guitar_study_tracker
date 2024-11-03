import inspect

# Global variable that turns the profile on or off.  It isn't currently used
use_profiler=True

class LogManager:
    """
    You shouldn't have to instantiate this class directly.  It is instantiated by the FunctionLogger class
    This is a singleton intended to keep track of the number of times the FunctionLogger class is instantiated.  If your application has FunctionLogger calls from multiple files, they will each be aware of the universal count through this class.
    
    """
    # used for singleton pattern
    _instance=None
    _profiler_counter=0
    _is_logger_on=True

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def get_counter(self):
        return self._profiler_counter
    
    def increment_counter(self):
        self._profiler_counter+=1

    def set_is_logger_on(self, logger_value):
        self._is_logger_on=logger_value

    def get_is_logger_on(self):
        return self._is_logger_on

class FunctionLogger():

    # rest of profiler data
    __namespace=None
    __show_line_numbers=None
    __callstack=None
    __call_offset=None
    __log_id=None

    def __init__(self, namespace='', customdata={}, show_line_numbers=True, call_offset=1):
        """
        This class init method should be called at the beginning of a function.  It will echo out the name of the function to the screen.  When the function goes out of scope this class will echo out that the function has been exited.  Intended for use with Shiny for Python server functions
        
        Parameters

        namespace
            (str): this is the value from session.ns if called within shiny server function

        customdata
            (dict): This is a dictionary of key:value pairs of additional information we want to present at time of logging.  It will be passed through to the console message.  Ex. {'my_val':5,'fruit':['apple','orange']}          

        show_line_numbers
            (bool): If True, this will add line number fo the parent call information, otherwise it will not.  Default = True

        call_offset
            (int): This is the number of calls we want to offset in the call stack in order to make sure the top level is the function we want to profile that instantiated this object.        
        
        Example usage:

        import profiler
        def server(input, output, session):
            
            def function2()
                logger.FunctionLogger(session.ns)
                # additional function logic here

            def function1():
                profiler.FunctionLogger(session.ns)
                function2()
                # additional function logic here
        
        """
        if FunctionLogger.isLoggerOn():
            #__concrete_init__(self, namespace='', customdata={}, show_line_numbers=True, call_offset=1)
            log_counter=LogManager()
            
            log_counter.increment_counter()
            self.__log_id = log_counter.get_counter()
            self.__namespace=namespace
            self.__show_line_numbers = show_line_numbers
            self.__callstack = inspect.stack()
            self.__call_offset = call_offset
            self.__customdata = customdata
            self.profile_func('in')


    def isLoggerOn():
        log_mgr = LogManager()
        return log_mgr.get_is_logger_on()
    
    def setLogger(toggle_value:bool):
        """
        Use this to turn the logger on or off.  toggle_value=True turns logger on.  toggle_value=False turns logger off.
        """
        log_mgr = LogManager()
        log_mgr.set_is_logger_on(toggle_value)

    def profile_func(self, direction="in"):    
        """
        This function will echo out the name of the function it was called from as well as the namespace (for use with shiny server and module functions).  It will also show information about the parent call.
        
        Parameters

        direction
            (str): one of ['in','out'].  If 'in', this will show the function name and the calling function.  If 'out' it will just show the function name and namespace.

        """
        assert direction in ['in','out'], f'direction attribute must be "in" or "out", but got "{direction}".'
        
        # calculate namespace_text to add.  It is '' by default
        namespace_text=''
        if self.__namespace:
            namespace_text = "namespace: "+str(self.__namespace)

        # calculate customdata_text to add.  It is '' by default
        customdata_text=''
        if any(self.__customdata):
            customdata_text = 'Additional customdata: '+str(self.__customdata)
        
        # calculate line_num_text to add.  It is '' by default
        line_num_text=''
        if self.__show_line_numbers:
            line_number = self.__callstack[self.__call_offset+1][2] # parent's calling line number
            line_code = self.__callstack[self.__call_offset+1][4][0].strip() # parent's calling line of code
            line_num_text= str(" -- line: "+str(line_number)+": "+line_code)
        called_func_name = self.__callstack[self.__call_offset+0][3]
        calling_func_name = self.__callstack[self.__call_offset+1][3]
        if direction=='in':
            print(f"****** {self.__log_id} {namespace_text} -- Entering {called_func_name} <- {calling_func_name} {line_num_text}.  {customdata_text}")
        else:
            print(f"****** {self.__log_id} -- Leaving {called_func_name}")

    def __del__(self):
        """
        This runs automatically when the program counter exits the scope of the function this object was created in.  It displays an exit message.
        """
        if FunctionLogger.isLoggerOn():
            self.profile_func("out")
