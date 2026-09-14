class BudgetModel {
  final int id;
  final String userId;
  final int categoryId;
  final double amount;
  final int month;
  final int year;
  final double alertThreshold;

  BudgetModel({
    required this.id,
    required this.userId,
    required this.categoryId,
    required this.amount,
    required this.month,
    required this.year,
    required this.alertThreshold,
  });

  factory BudgetModel.fromJson(Map<String, dynamic> json) {
    return BudgetModel(
      id: json['id'] as int,
      userId: json['user_id'] as String,
      categoryId: json['category_id'] as int,
      amount: (json['amount'] as num).toDouble(),
      month: json['month'] as int,
      year: json['year'] as int,
      alertThreshold: (json['alert_threshold'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'category_id': categoryId,
      'amount': amount,
      'month': month,
      'year': year,
      'alert_threshold': alertThreshold,
    };
  }
}

class AlertModel {
  final int categoryId;
  final String? categoryName;
  final double budgetLimit;
  final double spent;
  final double percentage;
  final String status; // normal, warning, exceeded

  AlertModel({
    required this.categoryId,
    this.categoryName,
    required this.budgetLimit,
    required this.spent,
    required this.percentage,
    required this.status,
  });

  factory AlertModel.fromJson(Map<String, dynamic> json) {
    return AlertModel(
      categoryId: json['category_id'] as int,
      categoryName: json['category_name'] as String?,
      budgetLimit: (json['budget_limit'] as num).toDouble(),
      spent: (json['spent'] as num).toDouble(),
      percentage: (json['percentage'] as num).toDouble(),
      status: json['status'] as String,
    );
  }
}
