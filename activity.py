
import logging

class ActivityMixin(object):
	def __init__(self):
		self.queue = set()

	def update_queue(self, benefit_id, confirm_id):
		for callback in self.queue:
			try:
				callback(benefit_id,confirm_id, self.company_id)
			except:
				logging.error("Error in callback", exc_info=True)
		self.queue = set()
		self.company_id = None




	def fetch_queue(self,callback,company_id):
		self.company_id = company_id
		self.queue.add(callback)
		

