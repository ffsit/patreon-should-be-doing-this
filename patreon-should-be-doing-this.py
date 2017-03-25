#!/usr/bin/env python
import os
import operator
import Tkinter,tkFileDialog as fileDialog

class PatreonEntry:
	"""Stores Patreon data, there can be as many pledges"""
	def __init__(self, email):
		self.start_date = ""
		self.first_name = ""
		self.last_name = ""
		self.pledges = []
		self.lifetime = 0
		self.email = email

	def get_total(self):
		return sum(self.pledges)

	def set_name(self, first_name, last_name):
		if self.first_name == "":
			self.first_name = first_name
		if self.last_name == "":
			self.last_name = last_name

	def add_pledge(self, pledge, index):
		if len(self.pledges) > index:
			raise Exception("Multiple pledges for the same patron in the same month: " + str(self.get_email()))
		while len(self.pledges) < index:
			self.pledges.append(0.0)
		self.pledges.append(pledge)

	def set_lifetime(self, amount):
		self.lifetime = max(self.lifetime, amount)

	def get_list_form(self):
		formatted_pledges = []
		for pledge in self.pledges:
			if pledge > 0:
				formatted_pledges.append("{:10.2f}".format(pledge).ljust(10))
			else:
				formatted_pledges.append("")
		return [self.first_name, self.last_name, self.email, self.start_date, "{:10.2f}".format(self.lifetime).ljust(10), "{:10.2f}".format(self.get_total()).ljust(10)] + formatted_pledges

class PatreonList(dict):
	"""Stores all the patreons in a dictionary keyed on their email adress"""
	def __missing__(self, key):
		return PatreonEntry(key)

	def get_csv(self):
		csv = []
		for key in self:
			csv.append(self[key].get_list_form())
		return csv


def readCSVFile(filename):
	csv = []
	escaped = False
	cur_cell = ""
	cur_row = []
	with open(filename, 'rb') as file:
		byte = file.read(1)
		while byte != "":
			if byte == "\"":
				escaped = not escaped
			elif byte == "," and not escaped:
				cur_row.append(cur_cell)
				cur_cell = ""
			elif byte == "\n" and not escaped:
				cur_row.append(cur_cell)
				csv.append(cur_row)
				cur_cell = ""
				cur_row = []
			else:
				cur_cell = cur_cell + byte
			byte = file.read(1)
	return csv

def writeCSVFile(csv, filename):
	with open(filename, 'w') as out:
		for row in csv:
			out.write('"' + '","'.join(row) + '"\n')

root = Tkinter.Tk()
root.withdraw()
filenames = fileDialog.askopenfilenames(parent=root, title='Choose csv files to consolidate', filetypes=[("CSV files", ".csv"),("All files", ".*")])
out_filename = os.path.join(os.path.dirname(__file__), 'consolidated_patreon_data.csv')
patreons = PatreonList()
for index, filename in enumerate(root.tk.splitlist(filenames)):
	csv = readCSVFile(filename)
	for row in csv:
		if len(row) == 15 and len(row[12]) == 19:
			p = patreons[row[2]]
			p.start_date = row[12]
			p.set_name(row[0], row[1])
			if(row[5] == "Processed"):
				p.add_pledge(float(row[3].replace(',','')), index)
			p.set_lifetime(float(row[4].replace(',','')))
			patreons[row[2]] = p
csv = patreons.get_csv()
csv.sort(key=operator.itemgetter(5,1,0), reverse=True)

header = ['First name', 'Last name', 'E-Mail', 'Start', 'Lifetime', 'Total Pledge', 'Individual Pledges separated by month']
csv.insert(0, header)
writeCSVFile(csv, out_filename)
