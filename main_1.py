from PlnFormat import PlnFormat
from InputFileLocator import InputFileLocator
from ExcelSheetReader import ExcelSheetReader
from ScheduleBuilder import ScheduleBuilder
from NbpRateClient import NbpRateClient
from B2BIncomeCalculator import B2BIncomeCalculator
from CreditAssessor import CreditAssessor
from BankOfferLoader import BankOfferLoader
from HouseholdLoader import HouseholdLoader
from MortgageCalculator import MortgageCalculator
from AnalizaKredytuHipotecznego import AnalizaKredytuHipotecznego
from MortgageReportPdf import MortgageReportPdf

def main():
	formatter = PlnFormat()
	locator = InputFileLocator()
	reader = ExcelSheetReader()
	builder = ScheduleBuilder()
	reference_rate = NbpRateClient()
	b2b_income = B2BIncomeCalculator()

	data_1 = formatter.formatter()
	data_2 = locator.locator()
	data_3 = reader.reader()
	data_4 = builder.builder()
	data_5 = reference_rate.reference_rate()
	data_6 = b2b_income.b2b_income()
	assessor = CreditAssessor(data_1)
	data_7 = assessor.assessor()
	offers = BankOfferLoader(data_2, data_3)
	data_8 = offers.offers()
	data_9 = offers.market()
	household = HouseholdLoader(data_2, data_3, data_6)
	data_10 = household.household()
	data_11 = household.project()
	calculator = MortgageCalculator(data_10, data_11, data_8, data_9, data_5, data_4, data_7)
	data_12 = calculator.calculator()
	result = AnalizaKredytuHipotecznego(data_12, data_1, data_6)
	result.show()
	def _on_result_zapisz(data_13):
		zapisany_pdf = MortgageReportPdf(data_13, data_1)
		zapisany_pdf.pdf_path()
	result.bind_action('zapisz', _on_result_zapisz)
	pass

if __name__ == "__main__":
	main()
