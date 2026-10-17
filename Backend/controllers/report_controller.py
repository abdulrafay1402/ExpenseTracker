from services import report_service


def get_dashboard(user_id, month=None, year=None):
    return report_service.get_dashboard(user_id, month=month, year=year)


def category_wise_report(user_id, month=None, year=None):
    return report_service.category_wise_report(user_id, month=month, year=year)


def monthly_trend(user_id, year=None):
    return report_service.monthly_trend(user_id, year=year)


def income_vs_expense(user_id, year=None):
    return report_service.income_vs_expense(user_id, year=year)


def monthly_summary(user_id, month=None, year=None):
    return report_service.monthly_summary(user_id, month=month, year=year)


def top_expenses(user_id, month=None, year=None):
    return report_service.top_expenses(user_id, month=month, year=year)
