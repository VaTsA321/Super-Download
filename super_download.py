import requests
import threading
from math import ceil
import sys
import os

class my_thread(threading.Thread):
	def __init__(self, tid, bytes_range, url, file_size):
		threading.Thread.__init__(self)
		self.tid = tid
		self.bytes_range = bytes_range
		self.url = url
		self.file_size = file_size
	
	def run(self):
		download_chunk(self.tid, self.bytes_range, self.url, self.file_size)	

def download_chunk(tid, bytes_range, url, file_size):
	(ll,ul) = bytes_range
	if ul > file_size - 1:
		ul = file_size - 1 
	header_dict = {'Range' : 'bytes=' + str(int(ll)) + '-' + str(int(ul))}
	r = requests.get(url, stream = True, headers=header_dict)
	#print r.headers, 'tno= ', tid
	f = open('part_' + str(tid), 'wb')
	for item in r.iter_content(1024):
		f.write(item)
	f.close()

def combine_files(parts, path):
	with open(path,'wb') as output:
		for part in parts:
			with open(part,'rb') as f:
				output.writelines(f.readlines())
			os.remove(part)

def super_download(url, path):
	res = requests.get(url, stream = True)
	#print res.headers
	file_size = float(res.headers['content-length'])
	num_threads = 64
	if not res.headers['accept-ranges']:
		num_threads = 1
	res.close()
	ceil_file_size = ceil(file_size/num_threads) * num_threads
	thread_list = []
	parts = []
	for t_no in range(num_threads):
		bytes_range = ((ceil_file_size/num_threads)*t_no, ((ceil_file_size/num_threads)*(t_no+1)) - 1)
		#print bytes_range
		#print bytes_range
		thd = my_thread(t_no, bytes_range, url, file_size)
		thd.start()
		parts.append('part_' + str(t_no))
		thread_list.append(thd)	
	for t in thread_list:
		t.join()
	combine_files(parts, path)

def main():
	if len(sys.argv) != 3:
		print 'usage: ' + sys.argv[0] + ' \'<url>\' \'<dir path including file name>\''
		sys.exit(1)
	url = sys.argv[1]
	path = sys.argv[2]
	print 'Downloading'
	super_download(url, path)		
	print 'Done'
	
if __name__ == '__main__':
	main()
