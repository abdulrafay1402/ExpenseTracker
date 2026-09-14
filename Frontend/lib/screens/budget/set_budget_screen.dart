import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../providers/budget_provider.dart';
import '../../providers/currency_provider.dart';

class SetBudgetScreen extends ConsumerStatefulWidget {
  const SetBudgetScreen({super.key});

  @override
  ConsumerState<SetBudgetScreen> createState() => _SetBudgetScreenState();
}

class _SetBudgetScreenState extends ConsumerState<SetBudgetScreen> {
  final _formKey = GlobalKey<FormState>();
  final _amountController = TextEditingController();
  final _thresholdController = TextEditingController(text: '80');
  int? _categoryId;
  DateTime _date = DateTime.now();
  bool _submitting = false;

  @override
  void dispose() {
    _amountController.dispose();
    _thresholdController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate() || _categoryId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a category')),
      );
      return;
    }
    setState(() => _submitting = true);

    await ref.read(budgetProvider.notifier).setBudget({
      'category_id': _categoryId,
      'amount': double.parse(_amountController.text),
      'month': _date.month,
      'year': _date.year,
      'alert_threshold': double.parse(_thresholdController.text),
    });

    setState(() => _submitting = false);
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Budget saved')),
      );
      context.pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    final catsAsync = ref.watch(expenseCategoriesProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Set Budget')),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            catsAsync.when(
              data: (cats) => DropdownButtonFormField<int>(
                initialValue: _categoryId,
                decoration: const InputDecoration(labelText: 'Category', border: OutlineInputBorder()),
                items: cats.map((c) => DropdownMenuItem(value: c.id, child: Text(c.name))).toList(),
                onChanged: (v) => setState(() => _categoryId = v),
              ),
              loading: () => const CircularProgressIndicator(),
              error: (e, _) => Text('Error: $e'),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _amountController,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: const InputDecoration(labelText: 'Budget Amount', border: OutlineInputBorder()),
              validator: (v) {
                if (v == null || v.isEmpty) return 'Enter amount';
                if ((double.tryParse(v) ?? 0) <= 0) return 'Must be positive';
                return null;
              },
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _thresholdController,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: const InputDecoration(labelText: 'Alert Threshold (%)', border: OutlineInputBorder()),
              validator: (v) {
                if (v == null || v.isEmpty) return 'Enter threshold';
                final n = double.tryParse(v) ?? 0;
                if (n < 1 || n > 100) return 'Must be 1-100';
                return null;
              },
            ),
            const SizedBox(height: 16),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.calendar_today),
              title: Text('${_date.month}/${_date.year}'),
              subtitle: const Text('Budget Month'),
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
            const SizedBox(height: 24),
            FilledButton(
              onPressed: _submitting ? null : _submit,
              child: _submitting
                  ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Text('Save Budget'),
            ),
          ],
        ),
      ),
    );
  }
}
