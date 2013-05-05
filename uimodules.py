import tornado.web

class BenefitModule(tornado.web.UIModule):
	def render(self, benefit):
		return self.render_string(
			"modules/benefit.html",
			benefit = benefit,
			)


class BenefitCoModule(tornado.web.UIModule):
	def render(self,benefit):
		return self.render_string(
			"modules/benefitco.html",
			benefit = benefit,
			)