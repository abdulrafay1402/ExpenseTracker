class TransactionModel {
  final int id;
  final String userId;
  final String type; // income or expense
  final int? categoryId;
  final double amount;
  final String currency;
  final double rateToBase;
  final String date;
  final String? description;
  final int? paymentMethodId;
  final String? createdAt;
  final int voided;

  TransactionModel({
    required this.id,
    required this.userId,
    required this.type,
    this.categoryId,
    required this.amount,
    required this.currency,
    required this.rateToBase,
    required this.date,
    this.description,
    this.paymentMethodId,
    this.createdAt,
    required this.voided,
  });

  factory TransactionModel.fromJson(Map<String, dynamic> json) {
    return TransactionModel(
      id: json['id'] as int,
      userId: json['user_id'] as String,
      type: json['type'] as String,
      categoryId: json['category_id'] as int?,
      amount: (json['amount'] as num).toDouble(),
      currency: json['currency'] as String,
      rateToBase: (json['rate_to_base'] as num).toDouble(),
      date: json['date'] as String,
      description: json['description'] as String?,
      paymentMethodId: json['payment_method_id'] as int?,
      createdAt: json['created_at'] as String?,
      voided: json['voided'] as int,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'type': type,
      'category_id': categoryId,
      'amount': amount,
      'currency': currency,
      'date': date,
      'description': description,
      'payment_method_id': paymentMethodId,
    };
  }

  Map<String, dynamic> toUpdateJson() {
    final map = <String, dynamic>{};
    map['type'] = type;
    if (categoryId != null) map['category_id'] = categoryId;
    map['amount'] = amount;
    map['currency'] = currency;
    map['date'] = date;
    if (description != null) map['description'] = description;
    if (paymentMethodId != null) map['payment_method_id'] = paymentMethodId;
    return map;
  }
}
