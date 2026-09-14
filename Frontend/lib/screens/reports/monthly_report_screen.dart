import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../../providers/report_provider.dart';

class MonthlyReportScreen extends ConsumerStatefulWidget {
  const MonthlyReportScreen({super.key});

  @override
  ConsumerState<MonthlyReportScreen> createState() => _MonthlyReportScreenState();
}

class _MonthlyReportScreenState extends ConsumerState<MonthlyReportScreen> {
  late int _year;

  @override
  void initState() {
    super.initState();
    _year = DateTime.now().year;
    Future.microtask(_loadData);
  }

  void _loadData() {
    ref.read(reportProvider.notifier).loadIncomeVsExpense(year: _year);
  }

  void _previousYear() {
    setState(() => _year--);
    _loadData();
  }

  void _nextYear() {
    if (_year >= DateTime.now().year) return;
    setState(() => _year++);
    _loadData();
  }

  bool get _isCurrentYear => _year == DateTime.now().year;

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(reportProvider);
    final report = state.incomeVsExpense;
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Monthly Report')),
      body: Column(
        children: [
          // Year navigation bar
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: theme.colorScheme.primaryContainer,
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                IconButton(
                  onPressed: _previousYear,
                  icon: const Icon(Icons.chevron_left),
                  tooltip: 'Previous year',
                ),
                Text(
                  '$_year',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: theme.colorScheme.onPrimaryContainer,
                  ),
                ),
                IconButton(
                  onPressed: _isCurrentYear ? null : _nextYear,
                  icon: const Icon(Icons.chevron_right),
                  tooltip: 'Next year',
                ),
              ],
            ),
          ),
          // Report content
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
                              Text('Could not load report',
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
                      )
                    : report == null || report.data.isEmpty
                        ? Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(Icons.bar_chart, size: 64, color: Colors.grey[300]),
                                const SizedBox(height: 12),
                                Text('No data for $_year',
                                    style: TextStyle(color: Colors.grey[600])),
                              ],
                            ),
                          )
                        : RefreshIndicator(
                            onRefresh: () async => _loadData(),
                            child: SingleChildScrollView(
                              physics: const AlwaysScrollableScrollPhysics(),
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                children: [
                                  SizedBox(
                                    height: 300,
                                    child: BarChart(
                                      BarChartData(
                                        barGroups: report.data.map((item) {
                                          return BarChartGroupData(
                                            x: item.month,
                                            barRods: [
                                              BarChartRodData(
                                                toY: item.income,
                                                color: Colors.green,
                                                width: 12,
                                              ),
                                              BarChartRodData(
                                                toY: item.expense,
                                                color: Colors.red,
                                                width: 12,
                                              ),
                                            ],
                                          );
                                        }).toList(),
                                        titlesData: FlTitlesData(
                                          bottomTitles: AxisTitles(
                                            sideTitles: SideTitles(
                                              showTitles: true,
                                              getTitlesWidget: (value, _) {
                                                final month =
                                                    value.toInt().clamp(1, 12);
                                                return Text(
                                                  DateFormat('MMM').format(
                                                      DateTime(_year, month)),
                                                  style: const TextStyle(
                                                      fontSize: 10),
                                                );
                                              },
                                            ),
                                          ),
                                          leftTitles: const AxisTitles(
                                            sideTitles: SideTitles(
                                                showTitles: true,
                                                reservedSize: 40),
                                          ),
                                          topTitles: const AxisTitles(
                                              sideTitles: SideTitles(
                                                  showTitles: false)),
                                          rightTitles: const AxisTitles(
                                              sideTitles: SideTitles(
                                                  showTitles: false)),
                                        ),
                                        borderData: FlBorderData(show: false),
                                        gridData: const FlGridData(show: true),
                                      ),
                                    ),
                                  ),
                                  const SizedBox(height: 16),
                                  const Row(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      _LegendItem(
                                          color: Colors.green, label: 'Income'),
                                      SizedBox(width: 16),
                                      _LegendItem(
                                          color: Colors.red, label: 'Expense'),
                                    ],
                                  ),
                                ],
                              ),
                            ),
                          ),
          ),
        ],
      ),
    );
  }
}

class _LegendItem extends StatelessWidget {
  final Color color;
  final String label;
  const _LegendItem({required this.color, required this.label});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(width: 12, height: 12, color: color),
        const SizedBox(width: 4),
        Text(label, style: const TextStyle(fontSize: 12)),
      ],
    );
  }
}
