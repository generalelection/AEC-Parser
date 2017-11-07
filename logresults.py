import os
import simplejson as json
from datetime import datetime

def saveRecentResults(timestamp):

	# check if file exists already

	jsonObj = []

	if os.path.exists('recentResults.json'):

		print "Results file exists, updating"

		with open('recentResults.json','r') as recentResultsFile:
			
			# Convert the results to a list of datetime objects

			tempList = []
			recentResults = json.load(recentResultsFile)
			for result in recentResults:
				tempList.append(datetime.strptime(result,"%Y%m%d%H%M%S"))

			# Sort it	

			tempList.sort(reverse=True)

			# Check if it's less than 20 and append the new timestamp

			if len(tempList) < 20:

				print "Less than twenty results, appending latest now"

				tempList.append(datetime.strptime(timestamp,"%Y%m%d%H%M%S"))
				tempList.sort(reverse=True)
				for temp in tempList:
					jsonObj.append(datetime.strftime(temp, '%Y%m%d%H%M%S'))	
				print jsonObj

			# If it's 20, remove the oldest timestamp, then append the new one	

			elif len(tempList) == 20:

				print "Twenty results, removing oldest and appending newest"

				del tempList[-1]
				tempList.append(datetime.strptime(timestamp,"%Y%m%d%H%M%S"))
				tempList.sort(reverse=True)
				for temp in tempList:
					jsonObj.append(datetime.strftime(temp, '%Y%m%d%H%M%S'))	
				print jsonObj
					
		# Write the new version
		newJson = json.dumps(jsonObj, indent=4)
		with open('recentResults.json','w') as fileOut:
				fileOut.write(newJson)				

		print "Finished saving results log locally"

	# Otherwise start a new file		

	else:
		print "No results file, making one now"
		jsonObj.append(timestamp)
		newJson = json.dumps(jsonObj, indent=4)
		with open('recentResults.json','w') as fileOut:
				fileOut.write(newJson)

		print "Finished creating results log"


# saveRecentResults()
