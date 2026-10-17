import 'package:expensemate_app/models/report_model.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('parses largest-expense report items', () {
    final expense = LargestExpenseModel.fromJson({
      'id': 8,
      'category_name': 'Travel',
      'base_amount': 15000,
      'currency': 'USD',
      'date': '2026-10-09',
      'description': 'Flight',
    });

    expect(expense.id, 8);
    expect(expense.categoryName, 'Travel');
    expect(expense.baseAmount, 15000);
    expect(expense.currency, 'USD');
    expect(expense.date, '2026-10-09');
    expect(expense.description, 'Flight');
  });
}
