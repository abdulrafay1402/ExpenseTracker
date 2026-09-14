import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../providers/transaction_provider.dart';
import '../../providers/currency_provider.dart';
import '../../widgets/transaction_tile.dart';
import '../../widgets/error_view.dart';

class TransactionListScreen extends ConsumerStatefulWidget {
  const TransactionListScreen({super.key});

  @override
  ConsumerState<TransactionListScreen> createState() => _TransactionListScreenState();
}

class _TransactionListScreenState extends ConsumerState<TransactionListScreen> {
  String? _typeFilter;
  final _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    Future.microtask(() => ref.read(transactionProvider.notifier).loadTransactions());
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _applyFilters() {
    ref.read(transactionProvider.notifier).loadTransactions(
          type: _typeFilter,
          search: _searchController.text.isEmpty ? null : _searchController.text,
        );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(transactionProvider);
    final catsAsync = ref.watch(categoriesProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Transactions'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => context.push('/transactions/add'),
          ),
        ],
      ),
      body: Column(
        children: [
          // Filters
          Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _searchController,
                    decoration: InputDecoration(
                      hintText: 'Search...',
                      prefixIcon: const Icon(Icons.search),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                      isDense: true,
                    ),
                    onSubmitted: (_) => _applyFilters(),
                  ),
                ),
                const SizedBox(width: 8),
                DropdownButton<String?>(
                  value: _typeFilter,
                  hint: const Text('All'),
                  items: const [
                    DropdownMenuItem(value: null, child: Text('All')),
                    DropdownMenuItem(value: 'income', child: Text('Income')),
                    DropdownMenuItem(value: 'expense', child: Text('Expense')),
                  ],
                  onChanged: (v) {
                    setState(() => _typeFilter = v);
                    _applyFilters();
                  },
                ),
              ],
            ),
          ),
          // List
          Expanded(
            child: state.isLoading
                ? const Center(child: CircularProgressIndicator())
                : state.error != null
                    ? Center(
                        child: Padding(
                          padding: const EdgeInsets.all(24),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.cloud_off, size: 48, color: Colors.grey[400]),
                              const SizedBox(height: 12),
                              Text('Could not load transactions',
                                  style: TextStyle(color: Colors.grey[600])),
                              const SizedBox(height: 12),
                              FilledButton.icon(
                                onPressed: _applyFilters,
                                icon: const Icon(Icons.refresh),
                                label: const Text('Retry'),
                              ),
                            ],
                          ),
                        ),
                      )
                    : state.transactions.isEmpty
                        ? const Center(child: Text('No transactions yet'))
                        : catsAsync.when(
                            data: (cats) {
                              final catMap = {for (final c in cats) c.id: c.name};
                              return RefreshIndicator(
                                onRefresh: () => ref
                                    .read(transactionProvider.notifier)
                                    .loadTransactions(type: _typeFilter),
                                child: ListView.separated(
                                  itemCount: state.transactions.length,
                                  separatorBuilder: (_, __) => const Divider(height: 1),
                                  itemBuilder: (context, i) {
                                    final tx = state.transactions[i];
                                    return TransactionTile(
                                      transaction: tx,
                                      categoryName: catMap[tx.categoryId],
                                      onTap: () => context.push('/transactions/${tx.id}'),
                                    );
                                  },
                                ),
                              );
                            },
                            loading: () => const Center(child: CircularProgressIndicator()),
                            error: (e, _) => ErrorView(
                              message: 'Error loading categories: $e',
                              onRetry: () => ref.invalidate(categoriesProvider),
                            ),
                          ),
          ),
        ],
      ),
    );
  }
}
