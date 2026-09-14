class DashboardModel {
  final double totalIncome;
  final double totalExpenses;
  final double remaining;
  final double? budgetPercentage;
  final String? topExpenseCategory;
  final int transactionCount;

  DashboardModel({
    required this.totalIncome,
    required this.totalExpenses,
    required this.remaining,
    this.budgetPercentage,
    this.topExpenseCategory,
    required this.transactionCount,
  });

  factory DashboardModel.fromJson(Map<String, dynamic> json) {
    return DashboardModel(
      totalIncome: (json['total_income'] as num).toDouble(),
      totalExpenses: (json['total_expenses'] as num).toDouble(),
      remaining: (json['remaining'] as num).toDouble(),
      budgetPercentage: json['budget_percentage'] != null
          ? (json['budget_percentage'] as num).toDouble()
          : null,
      topExpenseCategory: json['top_expense_category'] as String?,
      transactionCount: json['transaction_count'] as int,
    );
  }
}

class CategoryWiseItem {
  final String categoryName;
  final int categoryId;
  final double total;

  CategoryWiseItem({
    required this.categoryName,
    required this.categoryId,
    required this.total,
  });

  factory CategoryWiseItem.fromJson(Map<String, dynamic> json) {
    return CategoryWiseItem(
      categoryName: json['category_name'] as String,
      categoryId: json['category_id'] as int,
      total: (json['total'] as num).toDouble(),
    );
  }
}

class CategoryWiseReport {
  final int month;
  final int year;
  final List<CategoryWiseItem> categories;

  CategoryWiseReport({
    required this.month,
    required this.year,
    required this.categories,
  });

  factory CategoryWiseReport.fromJson(Map<String, dynamic> json) {
    return CategoryWiseReport(
      month: json['month'] as int,
      year: json['year'] as int,
      categories: (json['categories'] as List)
          .map((e) => CategoryWiseItem.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}

class MonthlyTrendItem {
  final int month;
  final String type;
  final double total;

  MonthlyTrendItem({
    required this.month,
    required this.type,
    required this.total,
  });

  factory MonthlyTrendItem.fromJson(Map<String, dynamic> json) {
    return MonthlyTrendItem(
      month: json['month'] as int,
      type: json['type'] as String,
      total: (json['total'] as num).toDouble(),
    );
  }
}

class MonthlyTrendReport {
  final int year;
  final List<MonthlyTrendItem> data;

  MonthlyTrendReport({required this.year, required this.data});

  factory MonthlyTrendReport.fromJson(Map<String, dynamic> json) {
    return MonthlyTrendReport(
      year: json['year'] as int,
      data: (json['data'] as List)
          .map((e) => MonthlyTrendItem.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}

class IncomeVsExpenseItem {
  final int month;
  final double income;
  final double expense;

  IncomeVsExpenseItem({
    required this.month,
    required this.income,
    required this.expense,
  });

  factory IncomeVsExpenseItem.fromJson(Map<String, dynamic> json) {
    return IncomeVsExpenseItem(
      month: json['month'] as int,
      income: (json['income'] as num).toDouble(),
      expense: (json['expense'] as num).toDouble(),
    );
  }
}

class IncomeVsExpenseReport {
  final int year;
  final List<IncomeVsExpenseItem> data;

  IncomeVsExpenseReport({required this.year, required this.data});

  factory IncomeVsExpenseReport.fromJson(Map<String, dynamic> json) {
    return IncomeVsExpenseReport(
      year: json['year'] as int,
      data: (json['data'] as List)
          .map((e) => IncomeVsExpenseItem.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}

class MonthlySummary {
  final int month;
  final int year;
  final double totalIncome;
  final double totalExpenses;
  final double remaining;
  final int transactionCount;
  final String? topExpenseCategory;
  final List<CategoryWiseItem> categoryBreakdown;

  MonthlySummary({
    required this.month,
    required this.year,
    required this.totalIncome,
    required this.totalExpenses,
    required this.remaining,
    required this.transactionCount,
    this.topExpenseCategory,
    required this.categoryBreakdown,
  });

  factory MonthlySummary.fromJson(Map<String, dynamic> json) {
    return MonthlySummary(
      month: json['month'] as int,
      year: json['year'] as int,
      totalIncome: (json['total_income'] as num).toDouble(),
      totalExpenses: (json['total_expenses'] as num).toDouble(),
      remaining: (json['remaining'] as num).toDouble(),
      transactionCount: json['transaction_count'] as int,
      topExpenseCategory: json['top_expense_category'] as String?,
      categoryBreakdown: (json['category_breakdown'] as List)
          .map((e) => CategoryWiseItem.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}
