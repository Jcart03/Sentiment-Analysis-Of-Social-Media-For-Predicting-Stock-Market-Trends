from PyQt6.QtCore import QObject, pyqtSignal
class ErrorHandler(QObject):
    
    """
    A singleton class that handles error message and confirmations
    
    Class is used to relay error messages or confirmation messages from the backend to the controllers
    this is done using PyQt6's pyqtSignal method which essentially opens a listening path with a specific code 
    this is then picked up in the controllers. This class is global and can be accessed anywhere in the application
    """
    error_signal=pyqtSignal(str, int)
    confirmation_signal=pyqtSignal(str)
    _initialized=False
    _instance = None
    _last_error = None
   
    def __new__(cls):
        """
        Neat piece of code to ensure that only one instance of the Errorhandler class is created
        
        this method uses the afformentioned singleton design pattern to guarantee that only one instance of
        the ErrorHandler class exists (meaning I dont have to pass the errorhandler as an object to every class down the pipeline)

        Args:
            cls: the class
        Returns:
            ErrorHandler: the singleton instance of the ErrorHandler class
        """
       
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    def __init__(self):
        """
            Initializes the Error Handler instance
            
            Method is called only once due to the __new__ method, initialises the QObject base class (signals and slots wont work without it)
        """
       
        if getattr(self, '_initialized', False):
            return
        super().__init__()
        self._initialized = True
                       
    
    
    def handle_error(self, error_message: str, error_code: int = 0):
        """Relays error messages from backend to the controllers

        Args:
            error_message (str):  error message string
            error_code (int, optional): int labelling error code, Defaults to 0.
        """
        if (error_message, error_code) == self._last_error:
            print("Duplicate error ignored")
            return
        self._last_error = (error_message, error_code)
        self.error_signal.emit(error_message, error_code)
        
    def send_confirmation(self, confirmation_message: str):
        """Relays confirmation messages from backend to the controllers

        Args:
            confirmation_message (str): confirmation message string
        """
        
        self.confirmation_signal.emit(confirmation_message)
        