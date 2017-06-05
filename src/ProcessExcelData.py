#################################################
#						#
# ProcessExcelData				#
#						#
# A basic single-threaded Python script to read #
# in an XLSX data file, converting the data to  #
# Python datatypes, and writing these into a    #
# specified table in the local MySQL database   #
#						#
#						#
# Created By: Shane Brennan			#
# Date: 20170605				#
# Version: 0.1					#
#						#
#################################################

import os
import sys
import csv
import json
import xlrd
import datetime
import sqlalchemy
from sqlalchemy import exc
from optparse import OptionParser

class ProcessExcelData:

	def __init__(self, configFilename, excelFilename, csvFlag, verboseFlag):
		""" 
		The constructor for the process excel data, containing
		the path to the JSON configuration file, which determines the 
		action to be taken (e.g., convert to CSV, write to MySQL DB, etc.) 
		as well as the path to the excel file to be parsed. 

		Args
		~~~~
		configFilename - The path to the JSON configuration filename.
		excelFilename  - The path to the input data file. 
		verboseFlag    - Verbose output during process.
		csvFlag        - Output the data as a CSV to the console.

		Returns
		~~~~~~~
		None, the file inserts the data into a MySQL database. 
		A completion notification is given at the end of the processing.
		"""

		# The verbose flag
		self.verbose = verboseFlag
		self.csvFlag = csvFlag

		# The database settings
		self.engine  = None
		self.db      = None
		self.config  = None

		# Setup the JSON config
		self.setupConfig(configFilename)

		# Read the Excel file
		self.readExcel(excelFilename)

		# Print the completion notice
		if not self.csvFlag:
			print 'Finished processing Excel file.'


	def setupConfig(self, configFilename):
		""" 
		Reads the setup from the JSON file, and 
		configures the access to the MySQL database. 
		"""

		# Read the config JSON file
		with open(configFilename) as configFile:
			self.config = json.load(configFile)

		# Instantiate the MySQL connection
		try:
			connectionString = "mysql://{0}:{1}@{2}/{3}".format(
					self.config['username'], 
					self.config['password'], 
					self.config['hostname'], 
					self.config['database'])

			if self.engine is None and self.db is None:
				self.engine = sqlalchemy.create_engine(connectionString)
				self.db = self.engine.connect()
			else:
				print 'Connection already exists...'
		except exc.SQLAlchemyError:
			print 'initConnection(), Error initializing database...'
			exit(1)

	def readExcel(self, excelFilename):
		""" 
		The readExcel() function takes the path to an XLSX file and 
		parses the data in the Excel file to insert in to a MySQL database.
		"""

		workbook = xlrd.open_workbook(excelFilename)
		worksheet = workbook.sheet_by_index(0)
		for rowIndex in xrange(worksheet.nrows):
			rowList = []
			for colIndex in xrange(worksheet.ncols):

				if rowIndex > 1:
					elementValue  = worksheet.cell_value(rowIndex, colIndex)
					elementType   = worksheet.cell_type(rowIndex, colIndex)

					if elementType == xlrd.XL_CELL_DATE:
    						dtTuple   = xlrd.xldate_as_tuple(elementValue, workbook.datemode)
						dtElement = datetime.datetime(
							    dtTuple[0], dtTuple[1], dtTuple[2],
							    dtTuple[3], dtTuple[4], dtTuple[5])
						rowList.append(dtElement.strftime('%Y-%m-%d'))
					elif elementType == xlrd.XL_CELL_NUMBER:
						intElement = int(elementValue)
						rowList.append(str(intElement))
					else:
						strElement = unicode(elementValue).encode('ascii','ignore')
						rowList.append(strElement)
			if self.csvFlag:
				print ','.join(rowList)
			else:
				if rowIndex > 1:
					self.insertRow(rowList)
			if rowIndex % 10000 == 0:
				self.commit()
		self.commit()

	def insertRow(self, rowList):

		sqlString =  'INSERT INTO conversions ('
		sqlString += 'week, site, visitcountry, '
		sqlString += 'entrypage, subtype, device, '
		sqlString += 'visits, signups, orders) '
		sqlString += 'VALUES ('
		sqlString += "'{0}', ".format(rowList[0])
		sqlString += "'{0}', ".format(rowList[1])
		sqlString += "'{0}', ".format(rowList[2])
		sqlString += "'{0}', ".format(rowList[3])
		sqlString += "'{0}', ".format(rowList[4])
		sqlString += "'{0}', ".format(rowList[5])
		sqlString += " {0},  ".format(rowList[6])
		sqlString += " {0},  ".format(rowList[7])
		sqlString += " {0}); ".format(rowList[8])

		try:
			self.db.execute(sqlString, tableName=self.config['tablename'])
		except exc.SQLAlchemyError, err:
			print 'ERROR - InsertRow() function'
			print err
			exit(1)
		except Exception, err:
			print 'ERROR - InsertRow() function'
			print err
			exit(1)

	def commit(self):
		try:
			self.db.execute("COMMIT;", tableName=self.config['tablename'])
		except exc.SQLAlchemyError, err:
			print err
		except Exception, err:
			print err

	def closeConnection(self):
		try:
			self.db.close()
			self.engine.dispose()
			self.db     = None
			self.engine = None
		except exc.SQLAlchemyError:
			self.logger.error('CreateReport, closeConnection(), Error closing database...')


	def removeEscapeChars(self, sqlInputText):
		if sqlInputText is None:
			return "NULL"
		elif len(sqlInputText) > 0:
			sqlText = sqlInputText.replace("'","\'\'")
			return sqlText
		else:
			return "NULL"

	def readFile(self, excelFilename, csvFilename, verboseFlag):
		# Set the verbose flag
		self.verbose = verboseFlag

		# Read in the Excel file as a list of lists
		workbook  = openpyxl.load_workbook(excelFilename, data_only=True)
		worksheet = workbook.worksheets[0]
		
		# Set the row and column limits for the first worksheet
		rowLimit = worksheet.max_row
		colLimit = worksheet.max_column

		if self.verbose:
			print 'Found {0} with {1} rows by {2} columns'.format(excelFilename, rowLimit, colLimit)

			# Print out the first five rows
			for x in xrange(1, 10):
				rowList = []
				for y in xrange(1, colLimit):
					worksheet.cell(row=x, column=y).value
					rowList.append(element)
				print ','.join(rowList)
		else:
			dataList = []
			for x in xrange(1, rowLimit):
				rowList = []
				for y in xrange(1, colLimit):
					element = worksheet.cell(row=x, column=y).value
					if element is None:
						rowList.append('')
					else: 
						try:
							rowList.append(element.encode('ascii', 'ignore'))
						except Exception, err:
							print 'Error reading',element
				dataList.append(rowList)

			# Now write the list data to CSV
			rowIndex = 0
			with open(csvFilename, 'wb') as csvFile:
				wr = csv.writer(csvFile, quoting=csv.QUOTE_ALL)
				for rowList in dataList:
					wr.writerow(rowList)
					rowIndex += 1

			print 'Wrote {0} lines to {1}'.format(rowIndex, csvFilename)


def main(argv):
	parser = OptionParser(usage="Usage: ProcessExcelData [-v|--verbose] <json-config> <excel-filename>")

        parser.add_option("-v", "--verbose",
                action="store_true",
                dest="verboseFlag",
                default=False,
                help="Verbose output from the script")

        parser.add_option("-c", "--csv",
                action="store_true",
                dest="csvFlag",
                default=False,
                help="Output CSV to the console")

	(options, filename) = parser.parse_args()

#	if len(filename) != 2 or not os.path.isfile(filename[0]) or not os.path.isfile(filename[1]):
#		print parser.print_help()
#		print len(filename)
#		print filename[0]
#		print filename[1]
#		print "Error - you need to provide a valid JSON config file and Excel data file as inputs"
#		exit(1)
#	elif '.json' not in filename[0].lower() or '.xlsx' not in filename[1].lower():
#		print parser.print_help()
#		print "Error - you need to provide a valid JSON config file and Excel data file as inputs in that order"
#		exit(1)

	excelParser = ProcessExcelData(filename[0], filename[1], options.csvFlag, options.verboseFlag)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
