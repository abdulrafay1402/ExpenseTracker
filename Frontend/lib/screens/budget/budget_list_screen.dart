import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../providers/budget_provider.dart';
import '../../providers/currency_provider.dart';
import '../../widgets/budget_progress_bar.dart';

class BudgetListScreen extends ConsumerStatefulWidget {
  const BudgetListScreen({super.key});

  @override
  ConsumerState<BudgetListScreen> createState() => _BudgetListScreenState();
}

class _BudgetListScreenState extends ConsumerState<BudgetListScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(_loadData);
  }

  Future<void> _loadData() async {
    final now = DateTime.now();
    await Future.wait([
      ref.read(budgetProvider.notifier).loadBudgets(month: now.month, year: now.year),
      ref.read(budgetProvider.notifier).loadAlerts(month: now.month, year: now.year),
    ]);
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(budgetProvider);
    final catsAsync = ref.watch(categoriesProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Budgets'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => context.push('/budget/set'),
          ),
        ],
      ),
      body: catsAsync.when(
        data: (cats) {
          final catMap = {for (final c in cats) c.id: c.name};
          final alertMap = {for (final a in state.alerts) a.categoryId: a};

          if (state.error != null && !state.isLoading) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.cloud_off, size: 48, color: Colors.grey[400]),
                    const SizedBox(height: 12),
                    Text('Could not load budgets',
                        style: TextStyle(color: Colors.grey[600])),
                    const SizedBox(height: 12),
                    FilledButton.icon(
                      onPressed: _loadData,
                      icon: const Icon(Icons.refresh),
                      label: const Text('Retry'),
                    ),
                  ],
                ),
              ),
            );
          }

          if (state.budgets.isEmpty && !state.isLoading) {
            return const Center(child: Text('No budgets set. Tap + to add one.'));
          }

          return state.isLoading
              ? const Center(child: CircularProgressIndicator())
              : RefreshIndicator(
                  onRefresh: _loadData,
                  child: ListView.builder(
                    itemCount: state.budgets.length,
                    itemBuilder: (context, i) {
                      final b = state.budgets[i];
                      final alert = alertMap[b.categoryId];
                      return BudgetProgressBar(
                        categoryName: catMap[b.categoryId] ?? 'Category ${b.categoryId}',
                        spent: alert?.spent ?? 0,
                        limit: b.amount,
                        status: alert?.status ?? 'normal',
                      );
                    },
                  ),
                );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text('Error loading categories: $e'),
              const SizedBox(height: 12),
              FilledButton.icon(
                onPressed: () => ref.invalidate(categoriesProvider),
                icon: const Icon(Icons.refresh),
                label: const Text('Retry'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
