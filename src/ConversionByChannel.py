import sys
import io
import re
import os
import csv
import datetime
import collections
from sets import Set
from scipy import stats
from optparse import OptionParser

class ConversionByChannel:

	def __init__(self, inputFilename, verboseFlag):
		self.verbose    = verboseFlag
		self.channels   = {}
		self.keys       = Set()

		self.readCSVFile(inputFilename)
		self.getConversions()

	def readCSVFile(self, inputFilename):
		""" Reads in the input CSV file provided and 
		    iterates through the process line by line. 
		"""
                inputFile            = open(inputFilename, 'rb');
                reader               = csv.reader(inputFile, delimiter=',')
                index                = 0

                for row in reader:
			if index > 0:
				week         = row[0]
				site         = row[1]
				visitCountry = row[2]
				entryPage    = row[3]
				subtype      = row[4]
				device       = row[5]
				visits       = row[6]
				signups      = row[7]
				dna          = row[8]

				key          = '{0},{1},{2},{3},{4}'.format(site, visitCountry, entryPage, subtype, device)
				channel = Channel(week, site, visitCountry, entryPage, subtype, device, visits, signups, dna)

				if key in self.keys:
					channelList = self.channels[key]
					channelList.append(channel)
					self.channels[key] = channelList
				else:
					if self.verbose:
						print 'Adding new key: {0}'.format(key)
					self.channels[key] = [ channel ]
					self.keys.add(key)
			index += 1

		if self.verbose:
			print 'Added {0} entries to {1} keys'.format(index, len(self.keys))


	def getConversions(self):

		for key in self.keys:

			channelList = self.channels[key]

			signups     = 0.0
			dna         = 0.0
			visits      = 0.0
			dateList    = []
			dnaList     = []
			signupsList = []

			for channel in channelList:
				visits   += channel.getVisits()
				signups  += channel.getSignups()
				dna      += channel.getDNA()
				dateList.append(channel.getTime())

				if visits > 0.0:
					signupsList.append(signups/visits)
					dnaList.append(dna/visits)
				else:
					signupsList.append(0.0)
					dnaList.append(0.0)


			if visits > 0.0:
				signupConv = float(signups) / float(visits)
				dnaConv    = float(dna) / float(visits)
				signupGradient, signupIntercept, r_value, p_value, std_err = stats.linregress(dateList,signupConv)
				dnaGradient, dnaIntercept, r_value, p_value, std_err = stats.linregress(dateList,dnaConv)

				if signupConv > 0.0 and signupConv < 1.0:
					print '{0},{1:.0f},{2:.0f},{3:.0f},{4:.5f},{5:.5f},{6:.5f},{7:.5f},{8:.5f},{9:.5f}'.format(key,
						visits,
						signups,
						dna,
						signupConv,
						dnaConv,
						signupGradient,
						signupIntercept,
						dnaGradient,
						dnaIntercept)

class Channel:

	def __init__(self, week, site, visitCountry, entryPage, subtype, device, visits, signups, dna):

		self.week         = week
		self.visits       = int(visits)
		self.signups      = int(signups)
		self.dna          = int(dna)

		if self.visits == 0:
			self.signupConversion = 0.0
			self.dnaConversion    = 0.0
		else:
			self.signupConversion = ( float(signups) / float(visits) )
			self.dnaConversion    = ( float(dna) / float(visits) )

	def getTime(self):
		dt = datetime.datetime.strptime(self.week,'%m/%d/%Y')
		return int(dt.strftime('%s'))

	def getSignupConversion(self):
		return self.signupConversion

	def getDNAConversion(self):
		return self.signupConversion

	def getVisits(self):
		return self.visits

	def getSignups(self):
		return self.signups

	def getDNA(self):
		return self.dna

def main(argv):
        parser = OptionParser(usage="Usage: ConversionByChannel <input-filename>")

        parser.add_option("-v", "--verbose",
                action="store_true",
                dest="verboseFlag",
                default=False,
                help="Verbose output.")

        (options, filename) = parser.parse_args()

	if len(filename) != 1:
                parser.print_help()
                print '\nYou need to provide one input file.'
                exit(1)

	if not os.path.exists(filename[0]):
                parser.print_help()
                print '\nYou need to provide an existing input file.'
                exit(1)

	conversions = ConversionByChannel(filename[0], options.verboseFlag)

if __name__ == "__main__":
    sys.exit(main(sys.argv))



