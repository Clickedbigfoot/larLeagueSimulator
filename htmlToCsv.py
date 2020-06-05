#!/usr/bin/python

"""
This script will read from an html file and convert it into a csv file.
The csv file will contain only the authors of each message, the message itself, and the time it was sent
"""

import argparse #Arguments and flags
import re #Good for finding

OUTPUT_FILE = "chat.csv"
DELIMITER = "|_|" #Delimiter in csv file

AUTHOR_INDIC = "chatlog__author-name" #Indication of the message author's name
TIME_INDIC = "chatlog__timestamp" #Indication of the message's timestamp
MESSAGE_INDIC = "class=\"markdown" #Indication of a message in the line
MESSAGE_LINK_INDIC = "markdown\"><a href=" #Indication of a link being the message
MESSAGE_IN_LINK_INDIC = "<a href" #Indication of a link in the middle of the text message
EMBED_LINK_INDIC = "chatlog__embed-" #Indication that this is just an embedded link title
IMAGE_INDIC = "chatlog__attachment\""

RE_MESSAGE = "markdown\">.*?</div" #Regex for finding a message
RE_AUTHOR = "author-name\" title=\".*?#\d\d\d\d" #Regex for finding author name
RE_TIME = "timestamp\">.*?</span" #Regex for finding the timestamp

IMG_SYMBOL = "$IMAGE$"
LINK_SYMBOL = "$LINK$"



"""
Returns the message of the line passed in
@param line: the string line passed in that holds the message
@return a string isolating the message
"""
def getMessage(line):
	if MESSAGE_IN_LINK_INDIC in line:
		return LINK_SYMBOL
	temp = re.findall(RE_MESSAGE, line)[0]
	if MESSAGE_LINK_INDIC in temp:
		return LINK_SYMBOL
	temp = temp[10:len(temp)-5]
	return temp

"""
Returns the author listed in the line passed in
@param line: the string line passed in that holds the author's name
@return a string isolating the author name
"""
def getAuthor(line):
	temp = re.findall(RE_AUTHOR, line)[0]
	temp = temp[20:len(temp)-5]
	return temp

"""
Returns the time listed in the line passed in
@param line: the string line passed in that holds the timestamp
@return a string isolating the timestamp
"""
def getTime(line):
	temp = re.findall(RE_TIME, line)[0]
	temp = temp[11:len(temp)-6]
	return temp

def main(args):
	inputFile = open(args.input, "r")
	lastUser = "" #Name of the last user to be mentioned in the log, so probably the user speaking now
	lastTime = "" #The last timestamp mentioned in the log, so probably the time of whatever message is being read now
	msgs = [] #List of messages to be logged
	message = "" #The message string to be added to the log
	i = 0 #int for iterating through lines
	j = 0 #int for combining messages that span multiple lines
	lines = inputFile.readlines()
	line = ""
	for i in range(0, len(lines)):
		#Iterate through indeces in the lines of the chat log
		j = i + 1 #Keep j at the next line
		line = lines[i]
		if line == "\n":
			#Empty line
			continue
		if IMAGE_INDIC in line:
			#There was an image sent into the chat
			msgs.append(author + DELIMITER + lastTime + DELIMITER + IMG_SYMBOL)
			continue
		if AUTHOR_INDIC in line:
			#There is an author listed in this line
			author = getAuthor(line)
		if TIME_INDIC in line:
			#There is a timestamp in this line
			lastTime = getTime(line)
		if (MESSAGE_INDIC in line) and (EMBED_LINK_INDIC not in line):
			#There is a message in this line
			while (">\n" not in line) or ("/em>\n" in line):
				#This line continues to the next one
				line = line[:len(line) - 1] + ". " + lines[j] #Combine with the next line
				j += 1
			message = getMessage(line)
			if len(message) > 1:
				#This is a valid message
				message = author + DELIMITER + lastTime + DELIMITER + message
				msgs.append(message)

	inputFile.close()
	#Save the output
	outputFile = open(OUTPUT_FILE, "w+")
	for msg in msgs:
		#Iterate through the messages in msgs
		outputFile.write(msg + "\n")
	outputFile.close()


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='HTML to CSV converter')
	parser.add_argument('-c', dest='input', type=str, default="logs/chatlog.html", help='Custom path for chat log html file. logs/chatlog.html by default')
	#parser.add_argument("-pca", action="store_true", dest="pca", help="Performs PCA on the data")
	args = parser.parse_args()
	main(args)