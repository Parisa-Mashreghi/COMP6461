from threading import Thread
import os
import subprocess

log_dir=os.getcwd()+'/parallel_test'

def send_request(url, port, i):
    process = subprocess.Popen(['python3', 'httpc.py', 'get', '-v', '-p', f'{port}', f'{url}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    result = process.communicate()
    with open(f'{log_dir}/process{i}.txt', 'w') as f:
       f.write(result[0])
 
# -------------------------------------------------------
# Main function
# -------------------------------------------------------
def main():
    # abs_dir = os.path.join(os.getcwd(), log_dir)
    print(log_dir)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    for i in range(0, 6):
        Thread(target=send_request, args=('http://localhost/course.json', 8082, i)).start()

if __name__ == "__main__":
    main()
