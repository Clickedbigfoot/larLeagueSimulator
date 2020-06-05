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
RE_EMOJI = "<img class=\"emoji.*?>" #Regex for finding emojis
RE_MENTION = "<span class=\"mention\".*?</span>" #Regex for finding mentions of other people
RE_MENTION_USER = "@.*?</span" #Regex for getting the name of the person mentioned
RE_SPANS = "<span.*?</span>" #Regex for getting all remaining spans

IMG_SYMBOL = "$IMAGE$"
LINK_SYMBOL = "$LINK$"
EMOJI_SYMBOL = " $EMOJI$ " #Add spaces so that they aren't sticking to eachother or other words

HTML_SYMBOLS = {"&#39;":"'", "&#225;":"á", "&#224;":"à", "&#226;":"â", "&#233;":"é", "&#232;":"è", "&#201;":"É", "&gt;":">", "&lt;":"<", "&quot;":"\"", "&amp;":"&", "&#171;":"«", "&#187;":"»", "&#231;":"ç", "&#241;":"ñ", "&#237;":"í", "&#251;":"û", "&#235;":"ë", "&#161;":"¡", "&#245;":"õ", "&#234;":"ê", "&#199;":"Ç", "&#236;":"ì", "&#246;":"ö"}



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

"""
Fixes buggy symbols
@param message: the message to be fixed
@return the fixed message
"""
def getRepairedSymbols(message):
	fixed = message
	for symb in HTML_SYMBOLS.keys():
		#Iterate through every symbol being buggy
		fixed = fixed.replace(symb, HTML_SYMBOLS[symb])
	fixed = fixed.replace("&#160;", "") #Idk what this is, but it doesn't belong here
	return fixed

"""
Cleans the message of any emojis or buggy punctuation
@param message: the message to be cleaned
@return the cleaned message
"""
def getCleaned(message):
	cleaned = message
	while len(re.findall(RE_EMOJI, cleaned)) > 0:
		#There is an emoji
		cleaned = cleaned.replace(re.findall(RE_EMOJI, cleaned)[0], EMOJI_SYMBOL)
	mention = "" #String for replacing mention spans in the message
	while len(re.findall(RE_MENTION, cleaned)) > 0:
		#There is a mention
		mention = re.findall(RE_MENTION_USER, re.findall(RE_MENTION, cleaned)[0])[0]
		mention = mention[:len(mention) - 6] #Now just the name of the mentioned person
		cleaned = cleaned.replace(re.findall(RE_MENTION, cleaned)[0], " " + mention + " ")
	while len(re.findall(RE_SPANS, cleaned)) > 0:
		#There is a span remaining
		cleaned = cleaned.replace(re.findall(RE_SPANS, cleaned)[0], "")
	#Now to replace bugged punctuation and accents
	cleaned = getRepairedSymbols(cleaned)
	return cleaned

"""
Creates a list of tokenized messages
@param inputList: list of strings where each string is a message's contents
@return list of strings
"""
def getTokenizedMessages(inputList):
	messages = [] #List of messages to return
	msg = "" #String of tokens in a message
	token = "" #Token to add to msg
	for contents in inputList:
		#Iterate through each message's contents
		msg = "" #Reset
		token = ""
		contents = getCleaned(contents) #Clean it up emojis and buggy punctuation
		for char in contents:
			#Iterate through every character in contents
			token = token + char
		msg = msg + token
		messages.append(msg)
	return messages

def main(args):
	#Start by extracting all the messages
	inputFile = open(args.input, "r")
	lastUser = "" #Name of the last user to be mentioned in the log, so probably the user speaking now
	lastTime = "" #The last timestamp mentioned in the log, so probably the time of whatever message is being read now
	msgs = [] #List of messages' contents
	samples = [] #List of samples
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
			msgs.append(IMG_SYMBOL)
			samples.append(getRepairedSymbols(author) + DELIMITER + lastTime)
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
				msgs.append(message)
				samples.append(getRepairedSymbols(author) + DELIMITER + lastTime)
	inputFile.close()

	#Tokenize the messages
	msgs = getTokenizedMessages(msgs)

	#Save the output
	outputFile = open(OUTPUT_FILE, "w+")
	for i in range(0, len(samples)):
		#Iterate through the indeces of samples
		samples[i] = samples[i] + DELIMITER + msgs[i]
		outputFile.write(samples[i] + "\n")
	outputFile.close()


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='HTML to CSV converter')
	parser.add_argument('-c', dest='input', type=str, default="logs/chatlog.html", help='Custom path for chat log html file. logs/chatlog.html by default')
	#parser.add_argument("-pca", action="store_true", dest="pca", help="Performs PCA on the data")
	args = parser.parse_args()
	main(args)