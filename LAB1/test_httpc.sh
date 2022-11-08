#!/bin/bash

# Usage: httpc.py (get|post|help) [-h "Key: Value"] [-d inline-data] [-f file] URL

# Command list (You can add your test at the of the list)
cmd_list=(
'python3 httpc.py post -h "Content-Type: application/json" -v -d "{"Assignment": 1}" "http://httpbin.org/post"'
'python3 httpc.py post -v -h "Content-Type: application/json" -f "data.json" "http://httpbin.org/post"'
'python3 httpc.py get -v "http://httpbin.org/get?course=networking&assignment=1"'
'python3 httpc.py get -v -o out.txt "http://httpbin.org/status/301"')

# files and directories
outdir='test'
tmp="$outdir/tmp_httpc.txt"
log="$outdir/log.txt"
result="$outdir/result.txt"

# initialization and constant variables
sep='------------------------------------------------------------------------------------'
check="grep \"HTTP/\" $tmp"
mkdir -p $outdir
echo '' > $log
echo '' > $result

# Run tests
cnt=1
for cmd in "${cmd_list[@]}"
do
  echo $sep >  $tmp
  echo "[$cnt] $cmd" >> $tmp
  eval $cmd >> $tmp
  
  echo $sep >> $result
  echo "[$cnt] $cmd" >> $result
  eval $check >> $result
  
  cat $tmp >> $log
  
  echo "cmd $cnt was finished"
  cnt=$((cnt + 1))
done

rm $tmp
echo $sep >>  $log
echo $sep >>  $result
echo -e "\nTests are finished!"
cat $result
echo -e "\nEnter 'cat $result' to show the short result."
echo -e "Enter 'cat $log' to see the detailed result.\n"

