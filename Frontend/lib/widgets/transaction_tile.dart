import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/transaction_model.dart';

class TransactionTile extends StatelessWidget {
  final TransactionModel transaction;
  final String? categoryName;
  final VoidCallback? onTap;

  const TransactionTile({
    super.key,
    required this.transaction,
    this.categoryName,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isIncome = transaction.type == 'income';
    final color = isIncome ? Colors.green : Colors.red;
    final prefix = isIncome ? '+' : '-';
    final formattedDate = DateFormat('MMM dd, yyyy').format(
      DateTime.parse(transaction.date),
    );

    return ListTile(
      leading: CircleAvatar(
        backgroundColor: color.withValues(alpha: 0.1),
        child: Icon(
          isIncome ? Icons.arrow_downward : Icons.arrow_upward,
          color: color,
        ),
      ),
      title: Text(
        transaction.description ?? categoryName ?? transaction.type,
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
      ),
      subtitle: Text(
        '${categoryName ?? ''} • $formattedDate',
        style: TextStyle(fontSize: 12, color: Colors.grey[600]),
      ),
      trailing: Text(
        '$prefix${NumberFormat.currency(symbol: '${transaction.currency} ', decimalDigits: 0).format(transaction.amount)}',
        style: TextStyle(
          fontWeight: FontWeight.bold,
          color: color,
          fontSize: 14,
        ),
      ),
      onTap: onTap,
    );
  }
}
