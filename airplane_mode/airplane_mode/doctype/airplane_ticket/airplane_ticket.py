import random

import frappe
from frappe import _
from frappe.model.document import Document


class AirplaneTicket(Document):
	def validate(self):
		self.calculate_total()
		self.remove_duplicates()
		self.check_capacity()

	def calculate_total(self):
		total = self.flight_price or 0

		for addon in self.add_ons:
			total += addon.amount or 0

		self.total_price = total

	def remove_duplicates(self):
		seen = []
		unique_rows = []

		for row in self.add_ons:
			if row.item not in seen:
				seen.append(row.item)
				unique_rows.append(row)

		self.set("add_ons", unique_rows)

	def before_submit(self):
		if self.status != "Boarded":
			frappe.throw("Ticket can be submitted only when status is Boarded")

	def before_insert(self):
		number = random.randint(1, 99)
		letter = random.choice(["A", "B", "C", "D", "E"])
		self.seat = f"{number}{letter}"

	def on_submit(self):
		self.status = "Completed"

	def check_capacity(self):
		flight = frappe.get_doc("Airplane Flight", self.flight)
		airplane = frappe.get_doc("Airplane", flight.airplane)

		booked_count = frappe.db.count(
			"Airplane Ticket",
			{
				"flight": self.flight,
				"docstatus": ["!=", 2],
			},
		)

		if booked_count >= airplane.capacity:
			frappe.throw(_("No seats available for this flight."))
