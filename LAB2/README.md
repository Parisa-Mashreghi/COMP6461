# HTTPFS application

## Run the server:
```bash
python3 httpfs.py -v -p 8082 -d .
```


## Sample commands for the client:
```bash
# Secure Access -> Bad Request
python3 httpc.py get  -v -p 8082 'http://localhost/../response.json'  

# Error Handling -> Not Found
python3 httpc.py get  -v -p 8082 'http://localhost/test/response.json' 

# Successful File Request
python3 httpc.py get  -v -p 8082 'http://localhost/README.md'  

# Successful Directory Request
python3 httpc.py get  -v -p 8082 'http://localhost/'   

# Test POST method with inline data
python3 httpc.py post -v -p 8082 -h 'Content-Type:application/json' -d '{"Assignment": 1}' 'http://localhost/ptest/ex_post_inline.json' 
python3 httpc.py get  -v -p 8082 'http://localhost/ptest/ex_post_inline.json'

# Test POST method with file
python3 httpc.py post -v -p 8082 -h 'Content-Type:application/json' -f 'README.md' 'http://localhost/ptest/readme.txt' 
python3 httpc.py get  -v -p 8082 'http://localhost/ptest/readme.txt'

# Create folder if it does not exist
python3 httpc.py post -v -p 8082 -h 'Content-Type:application/json' -d '{"Assignment": 1}' 'http://localhost/p1/p2/course.json'
python3 httpc.py get  -v -p 8082 'http://localhost/p1/p2/course.json'
```
