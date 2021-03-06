import sys
import argparse
import socket
import threading
import queue
import os
args = ""
output_file = None

task_queue = queue.Queue(10)

class ScanController (threading.Thread):
        
    def __init__(self, thread_id, port, timeout):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.port = port
        self.timeout = timeout

    def run(self):
        #print("running thread", self.thread_id)
        scan(self.port, self.timeout)

def scan(port, timeout):
    global exitFlag
    global task_queue

    exitFlag = False
    
    while not exitFlag:
        if not task_queue.empty():
            ip = task_queue.get()
            #print("Scanning {}:{}".format(ip, port))
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            try:
                s.connect((ip, int(port)))
                s.close()
                print(ip)
                if args.output is not None:
                    output_file.write(ip+"\n")
            except:
                pass


def load_queue(filename):
    global task_queue
    with open(filename, "r") as file:
        for ip in file:
            task_queue.put(ip.rstrip())
    #print("Queue Loaded")

def file_exists(filename):
    exists = os.path.isfile(filename)  # initial check   
    while exists is False:
        print("File does not exist, try again")
        file = input("[New File]: ")
        return file_exists(file)
    return exists

def main():
    global exitFlag
    global args
    global output_file

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-f', dest='file', action='store')
    parser.add_argument('-p', dest='port', action='store')
    parser.add_argument('-o', dest='output', action='store', default=None)
    parser.add_argument('--threads', dest='threads', action='store', default=1)
    parser.add_argument('--timeout', dest='timeout', action='store', default=3)
    args = parser.parse_args()

    filename = args.file
    savefile = args.output
    temp = file_exists(filename)
    threads = []
    if args.output is not None:
        output_file = open(args.output, 'w')
    num_threads = int(args.threads)
    port = int(args.port)
    timeout = int(args.timeout)


    for x in range(int(num_threads)):
        # Create new threads
        thread = ScanController(x, port, timeout)
        thread.start()
        threads.append(thread)
    try:
        load_queue(filename)
    except KeyboardInterrupt:
        #print("punch!")
        pass
    except Exception as e:
        #print(e)
        #print("Error on Line:{}".format(sys.exc_info()[-1].tb_lineno))
        pass
    try:
        while not task_queue.empty():
            pass
        # Notify threads it's time to exit
        exitFlag = True
        # Wait for all threads to complete
        for t in threads:
            t.join()
        #print ("All Done!")
    except Exception as e:
        #print(e)
        pass
    
    if args.output is not None:
        output_file.close() 

if __name__ == '__main__':
    main()
