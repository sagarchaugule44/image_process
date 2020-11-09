@ECHO OFF
SET PIPELINE_REMOTE_ROOT_PATH=%cd%
ECHO PIPELINE_REMOTE_ROOT_PATH
SET ENV_ROOT=%PIPELINE_REMOTE_ROOT_PATH%\venv
SET PYTHON_ROOT=%ENV_ROOT%\scripts
rem "A:\workspace\demo\image_process\venv\Scripts\activate"
SET source_path=A:\workspace\demo\image_process\source
SET PYTHONPATH=%PYTHONPATH%;%source_path%;%ENV_ROOT%
SET SCRIPT="A:\workspace\demo\image_process\source\image_process\ui\__init__.py"
SET PYEXE=%PYTHON_ROOT%\pythonw.exe

start "" %PYEXE%  %SCRIPT%

 

pause
exit