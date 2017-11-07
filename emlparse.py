import json
import xmltodict
import os


def convertPartyCode(partycode):
	partyCodes = {'LP':'LIB', 'NP':'NAT'}
	if partycode in partyCodes:
		return partyCodes[partycode]
	else:
		return partycode	

def candidate_party(candidate,candidateType):
	if candidateType == 'short':
		if 'eml:AffiliationIdentifier' in candidate:
			return candidate['eml:AffiliationIdentifier']['@ShortCode']
		else:
			return 'IND'
	if candidateType == 'long':
		if 'eml:AffiliationIdentifier' in candidate:
			return candidate['eml:AffiliationIdentifier']['eml:RegisteredName']
		else:
			return 'Independent'

def eml_to_JSON(eml_file, type, local,timestamp):
	
	#convert xml to json
	
	if local:
		elect_data = xmltodict.parse(open(eml_file))
	else:
		elect_data = xmltodict.parse(eml_file)	
	
	if type == "media feed":
	  
		#parse house of reps
		results_json = {}
		summary_json = {}
		electorates_list = []

		for election in elect_data['MediaFeed']['Results']['Election']:
			# House of Representative contests
			
			if 'House' in election:
				# National summary
				results_json['enrollment'] = int(election['House']['Analysis']['National']['Enrolment'])
				results_json['votesCountedPercent'] = float(election['House']['Analysis']['National']['FirstPreferences']['Total']['Votes']['@Percentage'])
				results_json['votesCounted'] = int(election['House']['Analysis']['National']['FirstPreferences']['Total']['Votes']['#text'])
				
				summary_json['enrollment'] = int(election['House']['Analysis']['National']['Enrolment'])
				summary_json['votesCountedPercent'] = float(election['House']['Analysis']['National']['FirstPreferences']['Total']['Votes']['@Percentage'])
				summary_json['votesCounted'] = int(election['House']['Analysis']['National']['FirstPreferences']['Total']['Votes']['#text'])

				# Division summaries

				for contest in election['House']['Contests']['Contest']:

					electorates_json = {}
					electorates_json['id'] = int(contest['PollingDistrictIdentifier']['@Id'])
					electorates_json['name'] = contest['PollingDistrictIdentifier']['Name']
					print contest['PollingDistrictIdentifier']['Name']
					electorates_json['state'] = contest['PollingDistrictIdentifier']['StateIdentifier']['@Id']
					electorates_json['enrollment'] = int(contest['Enrolment']['#text'])
					electorates_json['votesCounted'] = int(contest['FirstPreferences']['Total']['Votes']['#text'])
					candidates = contest['FirstPreferences']['Candidate']
					electorates_json['candidates'] = [
						{
							'candidate_id': int(candidate['eml:CandidateIdentifier']['@Id']),
							'candidate_name': candidate['eml:CandidateIdentifier']['eml:CandidateName'],
							'votesTotal': int(candidate['Votes']['#text']),
							'votesPercent': float(candidate['Votes']['@Percentage']),
							'party_short': convertPartyCode(candidate_party(candidate,'short')),
							'party_long':candidate_party(candidate,'long'),
							'incumbent':candidate['Incumbent']['#text']
						}
						for candidate in candidates
					]
					# print contest['TwoCandidatePreferred']
					if "@Restricted" not in contest['TwoCandidatePreferred'] and "@Maverick" not in contest['TwoCandidatePreferred']:
						twoCandidatePreferred = contest['TwoCandidatePreferred']['Candidate']
						electorates_json['twoCandidatePreferred'] = [
							{
								'candidate_id': int(candidate['eml:CandidateIdentifier']['@Id']),
								'candidate_name': candidate['eml:CandidateIdentifier']['eml:CandidateName'],
								'votesTotal': int(candidate['Votes']['#text']),
								'votesPercent': float(candidate['Votes']['@Percentage']),
								'swing':float(candidate['Votes']['@Swing']),
								'party_short': convertPartyCode(candidate_party(candidate,'short')),
								'party_long':candidate_party(candidate,'long')
							}
							for candidate in twoCandidatePreferred
						]

					elif "@Restricted" in contest['TwoCandidatePreferred']:
						electorates_json['twoCandidatePreferred'] = "Restricted"

					elif "@Maverick" in contest['TwoCandidatePreferred']:
						electorates_json['twoCandidatePreferred'] = "Maverick"						

					twoPartyPreferred = contest['TwoPartyPreferred']['Coalition']
					
					electorates_json['twoPartyPreferred'] = [
						{
							'coalition_id': int(coalition['CoalitionIdentifier']['@Id']),
							'coalition_long': coalition['CoalitionIdentifier']['CoalitionName'],
							'coalition_short': coalition['CoalitionIdentifier']['@ShortCode'],
							'votesTotal': int(coalition['Votes']['#text']),
							'votesPercent': float(coalition['Votes']['@Percentage']),
							'swing':float(coalition['Votes']['@Swing'])
						}
						for coalition in twoPartyPreferred
					]		

					# print electorates_json
					electorates_list.append(electorates_json)			

				# print electorates_list
				results_json['divisions'] = electorates_list

			if 'Senate' in election:
				pass


		newJson = json.dumps(results_json, indent=4)
		summaryJson = json.dumps(summary_json, indent=4)

		# Save the file locally

		with open('{timestamp}.json'.format(timestamp=timestamp),'w') as fileOut:
			print "saving results locally"
			fileOut.write(newJson)	

		with open('summaryResults.json','w') as fileOut:
			print "saving results locally"
			fileOut.write(summaryJson)		

		