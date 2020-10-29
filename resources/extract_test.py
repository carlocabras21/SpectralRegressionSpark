import csv

f = open("test.csv", "w")

n_lines = 1000

with open('spectral_data_class.csv') as csvfile:
	lines = csvfile.readlines()[:n_lines] 
	for line in lines:
		f.write(line)

f.close()
