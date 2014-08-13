ZEO-WinService
==============

A windows service script for ZEO. ZEO-WinService uses ``pywin32`` to wrap the ``runzeo.py`` into a Windows Service. 


Code
----

This script requires ``pywin32`` and ``ZEO`` to run. I do intend to put it on PyPi when I have the time

You can run from ``cmd`` as Administrator::

  > python zeo_winservice.py
  
you will be given the service options, as shown below::


  Usage: 'zeo_winservice.py [options] install|update|remove|start [...]|stop|restart [...]|debug [...]'
  Options for 'install' and 'update' commands only:
   --username domain\username : The Username the service is to run under
   --password password : The password for the username
   --startup [manual|auto|disabled|delayed] : How the service starts, default = manual
   --interactive : Allow the service to interact with the desktop.
   --perfmonini file: .ini file to use for registering performance monitor data
   --perfmondll file: .dll file to use when querying the service for
     performance data, default = perfmondata.dll
  Options for 'start' and 'stop' commands only:
   --wait seconds: Wait for the service to actually start or stop.
                   If you specify --wait with the 'stop' option, the service
                   and all dependent services will be stopped, each waiting
                   the specified period.
                   
                   
Installing the Service
----------------------

Before you try to install, make sure you are running ``cmd`` as Administrator.
To install such that it will start up automatically, try shown below::

  >python zeo_winservice.py --startup=auto install
  
This gives you the following screen with ZEO options::

  Installing service ZEO WinService
  Start the ZEO storage server.
  
  Usage: %s [-C URL] [-a ADDRESS] [-f FILENAME] [-h]
  
  Options:
  -C/--configuration URL -- configuration file or URL
  -a/--address ADDRESS -- server address of the form PORT, HOST:PORT, or PATH
                          (a PATH must contain at least one "/")
  -f/--filename FILENAME -- filename for FileStorage
  -t/--timeout TIMEOUT -- transaction timeout in seconds (default no timeout)
  -h/--help -- print this usage message and exit
  -m/--monitor ADDRESS -- address of monitor server ([HOST:]PORT or PATH)
  --pid-file PATH -- relative path to output file containing this process's pid;
                     default $(INSTANCE_HOME)/var/ZEO.pid but only if envar
                     INSTANCE_HOME is defined
  
  Unless -C is specified, -a and -f are required.
  
  Enter command line arguments for ZEO Service:
  
Now you are prompted with the different configurations for the ZEO Service that you can pass. One thing to note here
is that the **filename option has to absolute path, and not a relative path**.

An example command line argument is::

  Enter command line arguments for ZEO Service: -f D:\path\to\data\file.fs -a localhost:9999
  
Here I am specifying that ZEO be run with the ``file.fs`` on ``localhost`` port ``9999``. After installing the
script, you need to start it by::

  >python zeo_winservice.py start
  
You will also be able to access the service from ``task manager`` or the ``Windows Services`` app.


Logging
-------

The logs from the service are sent to the windows ``Event Log`` which can be accessed by opening
the ``Event Viewer``. Once you open the ``Event Viewer``, the logs can be found under::

  Event Viewer->Windows Logs->Application
  
The logs from this script can be found under ``ZEO WinService`` in the Source column.

Reference
---------

This documentation is based on my blog post on `ZEO as a Windows Service <http://gouthamanbalaraman.com/blog/zeo-as-a-windows-service.html>`_.

