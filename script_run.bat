@echo off
REM 

start "publisher" cmd /k python -u publisher.py
start "sub-1"     cmd /k python -u subscriber.py sub-1
start "sub-2"     cmd /k python -u subscriber.py sub-2
start "sub-3"     cmd /k python -u subscriber.py sub-3
start "sub-4"     cmd /k python -u subscriber.py sub-4