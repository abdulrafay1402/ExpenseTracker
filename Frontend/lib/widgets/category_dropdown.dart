import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/currency_provider.dart';

class CategoryDropdown extends ConsumerWidget {
  final int? selected;
  final String type; // 'income' or 'expense'
  final ValueChanged<int?> onChanged;

  const CategoryDropdown({
    super.key,
    required this.selected,
    required this.type,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final provider = type == 'income' ? incomeCategoriesProvider : expenseCategoriesProvider;
    final categoriesAsync = ref.watch(provider);

    return categoriesAsync.when(
      data: (categories) => DropdownButtonFormField<int>(
        initialValue: selected,
        decoration: const InputDecoration(
          labelText: 'Category',
          border: OutlineInputBorder(),
        ),
        items: categories
            .map((c) => DropdownMenuItem(value: c.id, child: Text(c.name)))
            .toList(),
        onChanged: onChanged,
      ),
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => Text('Error: $e'),
    );
  }
}
