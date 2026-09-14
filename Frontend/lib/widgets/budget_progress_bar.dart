import 'package:flutter/material.dart';

class BudgetProgressBar extends StatelessWidget {
  final String categoryName;
  final double spent;
  final double limit;
  final String status; // normal, warning, exceeded

  const BudgetProgressBar({
    super.key,
    required this.categoryName,
    required this.spent,
    required this.limit,
    required this.status,
  });

  Color get _statusColor {
    switch (status) {
      case 'exceeded':
        return Colors.red;
      case 'warning':
        return Colors.orange;
      default:
        return Colors.green;
    }
  }

  @override
  Widget build(BuildContext context) {
    final pct = limit > 0 ? (spent / limit).clamp(0.0, 1.0) : 0.0;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(categoryName, style: const TextStyle(fontWeight: FontWeight.w600)),
              Text(
                '${(pct * 100).toStringAsFixed(1)}%',
                style: TextStyle(color: _statusColor, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          const SizedBox(height: 6),
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: LinearProgressIndicator(
              value: pct,
              backgroundColor: Colors.grey[200],
              valueColor: AlwaysStoppedAnimation(_statusColor),
              minHeight: 10,
            ),
          ),
          const SizedBox(height: 4),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Spent: ${spent.toStringAsFixed(0)}',
                style: TextStyle(fontSize: 12, color: Colors.grey[600]),
              ),
              Text(
                'Limit: ${limit.toStringAsFixed(0)}',
                style: TextStyle(fontSize: 12, color: Colors.grey[600]),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
