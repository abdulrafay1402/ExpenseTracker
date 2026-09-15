import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../providers/transaction_provider.dart';
import '../../providers/report_provider.dart';
import '../../providers/budget_provider.dart';
import '../../services/budget_service.dart';
import '../../services/currency_service.dart';
import '../../widgets/currency_dropdown.dart';
import '../../widgets/category_dropdown.dart';

class AddTransactionScreen extends ConsumerStatefulWidget {
  const AddTransactionScreen({super.key});

  @override
  ConsumerState<AddTransactionScreen> createState() => _AddTransactionScreenState();
}

class _AddTransactionScreenState extends ConsumerState<AddTransactionScreen> {
  final _formKey = GlobalKey<FormState>();
  final _amountController = TextEditingController();
  final _descController = TextEditingController();
  String _type = 'expense';
  String? _currency = 'PKR';
  int? _categoryId;
  DateTime _date = DateTime.now();
  bool _submitting = false;

  @override
  void dispose() {
    _amountController.dispose();
    _descController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    // Re-entry guard: the button disable happens on the next frame, so a fast
    // double-tap could otherwise fire _submit twice and create a duplicate.
    if (_submitting) return;
    if (!_formKey.currentState!.validate()) return;

    if (_categoryId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a category')),
      );
      return;
    }

    setState(() => _submitting = true);

    final amount = double.parse(_amountController.text);
    final data = {
      'type': _type,
      'category_id': _categoryId,
      'amount': amount,
      'currency': _currency ?? 'PKR',
      'date': DateFormat('yyyy-MM-dd').format(_date),
      'description': _descController.text.isEmpty ? null : _descController.text,
    };

    // Budget check for expenses
    if (_type == 'expense') {
      try {
        final budgetService = BudgetService();
        final alert = await budgetService.checkAlert(
          _categoryId!,
          month: _date.month,
          year: _date.year,
        );
        // Convert to PKR first: spent and budgetLimit are in PKR (base
        // currency), but amount is in the selected currency — comparing them
        // raw let e.g. 100 SAR slip past a 5,000 PKR budget unchecked.
        double amountInPkr = amount;
        final currency = _currency ?? 'PKR';
        if (currency != 'PKR') {
          try {
            final rate = await CurrencyService().getRate(currency, 'PKR');
            amountInPkr = amount * rate.rate;
          } catch (_) {
            // Rate unavailable — backend re-checks and converts on submit.
          }
        }
        // Check if adding this amount would exceed the budget
        final wouldExceed = (alert.spent + amountInPkr) > alert.budgetLimit;
        if (wouldExceed && alert.budgetLimit > 0 && context.mounted) {
          final proceed = await showDialog<bool>(
            context: context,
            builder: (ctx) => AlertDialog(
              icon: Icon(Icons.warning_amber_rounded,
                  color: Colors.red[400], size: 48),
              title: const Text('Budget Exceeded'),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'This expense will exceed your budget for ${alert.categoryName ?? 'this category'}.',
                    style: const TextStyle(fontWeight: FontWeight.w500),
                  ),
                  const SizedBox(height: 12),
                  _budgetRow('Budget Limit', alert.budgetLimit),
                  _budgetRow('Already Spent', alert.spent),
                  _budgetRow('This Expense (PKR)', amountInPkr),
                  const Divider(height: 16),
                  _budgetRow(
                    'Total After',
                    alert.spent + amountInPkr,
                    color: Colors.red,
                    bold: true,
                  ),
                  _budgetRow(
                    'Over By',
                    (alert.spent + amountInPkr) - alert.budgetLimit,
                    color: Colors.red,
                    bold: true,
                  ),
                ],
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(ctx, false),
                  child: const Text('Cancel'),
                ),
                FilledButton(
                  onPressed: () => Navigator.pop(ctx, true),
                  style: FilledButton.styleFrom(backgroundColor: Colors.red),
                  child: const Text('Add Anyway'),
                ),
              ],
            ),
          );
          if (proceed != true) {
            setState(() => _submitting = false);
            return;
          }
        }
      } catch (_) {
        // If budget check fails, proceed without warning
      }
    }

    try {
      await ref.read(transactionProvider.notifier).addTransaction(data);
      final state = ref.read(transactionProvider);
      if (state.error != null) {
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Failed: ${state.error}')),
          );
        }
      } else {
        // Refresh dashboard + budget alerts so the totals are up to date the
        // moment we return — the dashboard sits in an IndexedStack (bottom
        // nav) and never re-runs initState, so it would otherwise keep
        // showing pre-add numbers.
        final now = DateTime.now();
        ref
            .read(reportProvider.notifier)
            .loadDashboard(month: now.month, year: now.year);
        ref
            .read(budgetProvider.notifier)
            .loadAlerts(month: now.month, year: now.year);
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Transaction added')),
          );
          context.pop();
        }
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  Widget _budgetRow(String label, double value,
      {Color? color, bool bold = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 13)),
          Text(
            NumberFormat.currency(symbol: 'PKR ', decimalDigits: 0)
                .format(value),
            style: TextStyle(
              fontSize: 13,
              fontWeight: bold ? FontWeight.bold : FontWeight.w500,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Add Transaction')),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Type toggle
            SegmentedButton<String>(
              segments: const [
                ButtonSegment(
                    value: 'expense',
                    label: Text('Expense'),
                    icon: Icon(Icons.arrow_upward)),
                ButtonSegment(
                    value: 'income',
                    label: Text('Income'),
                    icon: Icon(Icons.arrow_downward)),
              ],
              selected: {_type},
              onSelectionChanged: (v) => setState(() {
                _type = v.first;
                _categoryId = null;
              }),
            ),
            const SizedBox(height: 16),
            // Amount
            TextFormField(
              controller: _amountController,
              keyboardType:
                  const TextInputType.numberWithOptions(decimal: true),
              decoration: const InputDecoration(
                labelText: 'Amount',
                prefixText: '  ',
                border: OutlineInputBorder(),
              ),
              validator: (v) {
                if (v == null || v.isEmpty) return 'Enter amount';
                final n = double.tryParse(v);
                if (n == null || n <= 0) return 'Invalid amount';
                return null;
              },
            ),
            const SizedBox(height: 16),
            // Currency
            CurrencyDropdown(
              selected: _currency,
              onChanged: (v) => setState(() => _currency = v),
            ),
            const SizedBox(height: 16),
            // Category
            CategoryDropdown(
              selected: _categoryId,
              type: _type,
              onChanged: (v) => setState(() => _categoryId = v),
            ),
            const SizedBox(height: 16),
            // Date
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.calendar_today),
              title: Text(DateFormat('MMM dd, yyyy').format(_date)),
              subtitle: const Text('Date'),
              onTap: () async {
                final picked = await showDatePicker(
                  context: context,
                  initialDate: _date,
                  firstDate: DateTime(2020),
                  lastDate: DateTime(2030),
                );
                if (picked != null) setState(() => _date = picked);
              },
            ),
            const SizedBox(height: 16),
            // Description
            TextFormField(
              controller: _descController,
              decoration: const InputDecoration(
                labelText: 'Description (optional)',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 24),
            FilledButton(
              onPressed: _submitting ? null : _submit,
              child: _submitting
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child:
                          CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('Save Transaction'),
            ),
          ],
        ),
      ),
    );
  }
}
