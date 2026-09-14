import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../providers/report_provider.dart';
import '../../providers/budget_provider.dart';
import '../../widgets/summary_card.dart';
import '../../widgets/budget_progress_bar.dart';

class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({super.key});

  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(_loadData);
  }

  Future<void> _loadData() async {
    final now = DateTime.now();
    await Future.wait([
      ref.read(reportProvider.notifier).loadDashboard(month: now.month, year: now.year),
      ref.read(budgetProvider.notifier).loadAlerts(month: now.month, year: now.year),
    ]);
  }

  @override
  Widget build(BuildContext context) {
    final report = ref.watch(reportProvider);
    final budgetState = ref.watch(budgetProvider);
    final fmt = NumberFormat.currency(symbol: 'PKR ', decimalDigits: 0);

    return Scaffold(
      appBar: AppBar(title: const Text('Dashboard')),
      body: report.isLoading
          ? const Center(child: CircularProgressIndicator())
          : report.error != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.cloud_off, size: 64, color: Colors.grey[400]),
                        const SizedBox(height: 16),
                        Text(
                          'Could not load data',
                          style: TextStyle(fontSize: 18, color: Colors.grey[600]),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          report.error!,
                          style: TextStyle(fontSize: 12, color: Colors.grey[500]),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 16),
                        FilledButton.icon(
                          onPressed: _loadData,
                          icon: const Icon(Icons.refresh),
                          label: const Text('Retry'),
                        ),
                      ],
                    ),
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadData,
                  child: SingleChildScrollView(
                    physics: const AlwaysScrollableScrollPhysics(),
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Summary cards
                        GridView.count(
                          crossAxisCount: 2,
                          shrinkWrap: true,
                          physics: const NeverScrollableScrollPhysics(),
                          childAspectRatio: 1.6,
                          children: [
                            SummaryCard(
                              title: 'Income',
                              value: fmt.format(report.dashboard?.totalIncome ?? 0),
                              icon: Icons.arrow_downward,
                              color: Colors.green,
                            ),
                            SummaryCard(
                              title: 'Expenses',
                              value: fmt.format(report.dashboard?.totalExpenses ?? 0),
                              icon: Icons.arrow_upward,
                              color: Colors.red,
                            ),
                            SummaryCard(
                              title: 'Remaining',
                              value: fmt.format(report.dashboard?.remaining ?? 0),
                              icon: Icons.account_balance_wallet,
                              color: Colors.blue,
                            ),
                            SummaryCard(
                              title: 'Transactions',
                              value: '${report.dashboard?.transactionCount ?? 0}',
                              icon: Icons.receipt_long,
                              color: Colors.purple,
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        // Top category and budget %
                        if (report.dashboard?.topExpenseCategory != null)
                          Card(
                            child: ListTile(
                              leading: const Icon(Icons.star, color: Colors.amber),
                              title: const Text('Top Expense Category'),
                              subtitle: Text(report.dashboard!.topExpenseCategory!),
                            ),
                          ),
                        if (report.dashboard?.budgetPercentage != null)
                          Card(
                            child: Padding(
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Text('Budget Usage',
                                      style: TextStyle(fontWeight: FontWeight.bold)),
                                  const SizedBox(height: 8),
                                  LinearProgressIndicator(
                                    value: (report.dashboard!.budgetPercentage! / 100)
                                        .clamp(0.0, 1.0),
                                    backgroundColor: Colors.grey[200],
                                    minHeight: 10,
                                    valueColor: AlwaysStoppedAnimation(
                                      report.dashboard!.budgetPercentage! >= 90
                                          ? Colors.red
                                          : report.dashboard!.budgetPercentage! >= 70
                                              ? Colors.orange
                                              : Colors.green,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                      '${report.dashboard!.budgetPercentage!.toStringAsFixed(1)}% used'),
                                ],
                              ),
                            ),
                          ),
                        const SizedBox(height: 16),
                        // Budget alerts
                        if (budgetState.alerts.isNotEmpty) ...[
                          const Text('Budget Alerts',
                              style:
                                  TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                          const SizedBox(height: 8),
                          ...budgetState.alerts.map(
                            (alert) => BudgetProgressBar(
                              categoryName:
                                  alert.categoryName ?? 'Category ${alert.categoryId}',
                              spent: alert.spent,
                              limit: alert.budgetLimit,
                              status: alert.status,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
    );
  }
}
