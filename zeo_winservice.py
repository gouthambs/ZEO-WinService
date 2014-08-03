__author__ = 'Gouthaman Balaraman'
__version__ = '0.1.0'
 
 
import sys
import os
import win32event
import win32service
import win32serviceutil
import win32api
import win32con
import logging
import servicemanager
from ZEO.runzeo import ZEOOptions, ZEOServer
from ZEO.runzeo import logger as zeo_logger
from ZEO.runzeo import __doc__ as zeo_doc
 
 
class NTLogHandler(logging.Handler):
    _log_map_ = {logging.INFO: servicemanager.LogInfoMsg,
                 logging.DEBUG: servicemanager.LogInfoMsg,
                 logging.NOTSET: servicemanager.LogInfoMsg,
                 logging.WARN: servicemanager.LogWarningMsg,
                 logging.WARNING: servicemanager.LogWarningMsg,
                 logging.ERROR: servicemanager.LogErrorMsg,
                 logging.FATAL: servicemanager.LogErrorMsg,
                 logging.CRITICAL: servicemanager.LogErrorMsg}
 
    def __init__(self):
        logging.Handler.__init__(self)
 
    def emit(self,record):
        msg = self.format(record)
        level_no = record.levelno
        log_func = self._log_map_[level_no]
        log_func(msg)
 
    def close(self):
        pass
 
 
zeo_args_regkey_name = "ZEOServiceArguments"
 
def get_registry_parameters(servicename):
    key = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, "System\\CurrentControlSet\\Services\\"+servicename)
    try:
        try:
            (command_line, regtype) = win32api.RegQueryValueEx(key,zeo_args_regkey_name)
            return command_line
        except:
            pass
    finally:
        key.Close()
 
    create_registry_parameters(servicename, zeo_args_regkey_name)
    return ""
 
 
def create_registry_parameters(servicename, parameters):
    new_key = win32api.RegOpenKeyEx(win32con.HKEY_LOCAL_MACHINE, 
                                    "System\\CurrentControlSet\\Services\\"+servicename,0,win32con.KEY_ALL_ACCESS)
    try:
        win32api.RegSetValueEx(new_key, zeo_args_regkey_name, 0, win32con.REG_SZ, parameters)
    finally:
        new_key.Close()
 
class ZEOService(win32serviceutil.ServiceFramework):
    _svc_name_ = "ZEO WinService"
    _svc_display_name_ = "ZEO Database Service"
    _svc_description_ = "This runs the ZEO server as a Windows service."
 
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self._setup_logging()
        self.s = None
        self.logger.info("Initializing ZEO Windows Service...")
 
    def SvcStop(self):
        try:
            self.logger.info("Stopping ZEO Windows service...")
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            self.s.server.close()
            self.s.clear_socket()
            self.s.remove_pidfile()
        finally:
            win32event.SetEvent(self.hWaitStop)
 
    def SvcDoRun(self):
        self.main()
 
    def main(self):
        try:
            args = get_registry_parameters(self._svc_name_)
            self.logger.info("Starting ZEO service with args %s ..."%args)
            options = ZEOOptions()
            args = args.split()
            options.realize(args)
            self.s = ZEOServer(options)
            self.s.check_socket()
            self.s.clear_socket()
            self.s.make_pidfile()
            self.s.open_storages()
            self.s.setup_signals()
            self.s.create_server()
            self.s.server.start_thread()
            self.logger.info("Started ZEO server")
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        except Exception as e:
            self.logger.exception(str(e))
 
 
 
    @classmethod
    def CustomOptionHandler(cls, opts):
        print zeo_doc
        args = raw_input("Enter command line arguments for %s: " % cls._svc_name_)
        try:
            create_registry_parameters(cls._svc_name_, args.strip())
        except Exception,x:
            print "Error occurred when setting command line args in the registry: ",x
        try:
            cls._svc_description_
        except LookupError:
            return
 
        key = win32api.RegCreateKey(win32con.HKEY_LOCAL_MACHINE,
            "System\\CurrentControlSet\\Services\\%s" % cls._svc_name_)
        try:
            win32api.RegSetValueEx(key, "Description", 0, win32con.REG_SZ, cls._svc_description_);
        finally:
            win32api.RegCloseKey(key)
 
    def _setup_logging(self):
        self.logger = logging.getLogger("ZEO.WinService")
        log_handler = NTLogHandler()
        FORMAT = '%(levelname)s | %(name)s | %(message)s'
        formatter = logging.Formatter(fmt=FORMAT)
        log_handler.setFormatter(formatter)
        self.logger.setLevel(logging.INFO)
        zeo_logger.setLevel(logging.WARNING)
        root = logging.getLogger()
        root.addHandler(log_handler)
 
def main():
    if win32serviceutil.HandleCommandLine(ZEOService, customOptionHandler=ZEOService.CustomOptionHandler) != 0:
        return
    if sys.argv[1] in ("install", "update"):
        print "\nYou can configure the command line arguments in the Registry as well."
        print "The key is: HKLM\\System\\CurrentControlSet\\Services\\%s" % ZEOService._svc_name_
        print "The value under that key is:  ", zeo_args_regkey_name
        args = get_registry_parameters(ZEOService._svc_name_)
        if args:
            print "(it is currently set to:  '%s')" % args
        else:
            print "(it is currently not set)"
 
 
 
if __name__ == '__main__':
    main()
