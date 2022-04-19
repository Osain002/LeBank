import random



class Details:
	def sort_code():
		num = str(random.randint(120000,129999))
		sortCode = '12' +'-'+ num[2]+num[3] + '-' +num[4] + num[5]
		return sortCode

	def account_number():
		return str(random.randint(10000000,99999999))


	sort_code = sort_code()
	account_number = account_number()



