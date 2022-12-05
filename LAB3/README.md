# Requirements
1. Python 3+

# Usage

1. Step 1: Run the router after compiling from the source or uncompressing the zip file
   ./router --port=3000 --drop-rate=0.0 --max-delay=50ms --seed=1

2. Step 2: Run the server
   python3 httpfs.py -v -p 8007 -d .

3. Step 3: Run the client
   python3 httpc.py get -v -p 8007 'http://localhost/README.md'
   python3 httpc.py get -v -p 8007 'http://localhost/'
   python3 httpc.py post -v -p 8007 -h 'Content-Type:application/json' -f 'libhttp.py' 'http://localhost/ptest/exec_post_libhttp.py'
   python3 test_concurrent.py


