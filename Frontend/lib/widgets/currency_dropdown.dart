import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/currency_provider.dart';

class CurrencyDropdown extends ConsumerWidget {
  final String? selected;
  final ValueChanged<String?> onChanged;

  const CurrencyDropdown({
    super.key,
    required this.selected,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currenciesAsync = ref.watch(currenciesProvider);

    return currenciesAsync.when(
      data: (currencies) => DropdownButtonFormField<String>(
        initialValue: selected,
        decoration: const InputDecoration(
          labelText: 'Currency',
          border: OutlineInputBorder(),
        ),
        items: currencies
            .map((c) => DropdownMenuItem(value: c.code, child: Text('${c.code} - ${c.name}')))
            .toList(),
        onChanged: onChanged,
      ),
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => Text('Error: $e'),
    );
  }
}
