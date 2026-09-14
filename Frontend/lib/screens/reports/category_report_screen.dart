import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../../providers/report_provider.dart';

class CategoryReportScreen extends ConsumerStatefulWidget {
  const CategoryReportScreen({super.key});

  @override
  ConsumerState<CategoryReportScreen> createState() => _CategoryReportScreenState();
}

class _CategoryReportScreenState extends ConsumerState<CategoryReportScreen> {
  late int _month;
  late int _year;

  @override
  void initState() {
    super.initState();
    final now = DateTime.now();
    _month = now.month;
    _year = now.year;
    Future.microtask(_loadData);
  }

  void _loadData() {
    ref.read(reportProvider.notifier).loadCategoryWise(month: _month, year: _year);
  }

  void _previousMonth() {
    setState(() {
      _month--;
      if (_month < 1) {
        _month = 12;
        _year--;
      }
    });
    _loadData();
  }

  void _nextMonth() {
    final now = DateTime.now();
    // Don't go past current month
    if (_year == now.year && _month == now.month) return;
    setState(() {
      _month++;
      if (_month > 12) {
        _month = 1;
        _year++;
      }
    });
    _loadData();
  }

  bool get _isCurrentMonth {
    final now = DateTime.now();
    return _year == now.year && _month == now.month;
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(reportProvider);
    final report = state.categoryWise;
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Category Report')),
      body: Column(
        children: [
          // Month navigation bar
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: theme.colorScheme.primaryContainer,
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                IconButton(
                  onPressed: _previousMonth,
                  icon: const Icon(Icons.chevron_left),
                  tooltip: 'Previous month',
                ),
                Text(
                  DateFormat('MMMM yyyy').format(DateTime(_year, _month)),
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: theme.colorScheme.onPrimaryContainer,
                  ),
                ),
                IconButton(
                  onPressed: _isCurrentMonth ? null : _nextMonth,
                  icon: const Icon(Icons.chevron_right),
                  tooltip: 'Next month',
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
                    : report == null || report.categories.isEmpty
                        ? Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(Icons.pie_chart_outline, size: 64, color: Colors.grey[300]),
                                const SizedBox(height: 12),
                                Text('No data for this month',
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
                                    height: 250,
                                    child: PieChart(
                                      PieChartData(
                                        sections: report.categories
                                            .asMap()
                                            .entries
                                            .map((entry) {
                                          final colors = [
                                            Colors.blue,
                                            Colors.red,
                                            Colors.green,
                                            Colors.orange,
                                            Colors.purple,
                                            Colors.teal,
                                            Colors.pink,
                                            Colors.amber,
                                            Colors.cyan,
                                            Colors.indigo,
                                          ];
                                          return PieChartSectionData(
                                            value: entry.value.total,
                                            title:
                                                '${entry.value.total.toStringAsFixed(0)}',
                                            color:
                                                colors[entry.key % colors.length],
                                            radius: 100,
                                            titleStyle: const TextStyle(
                                                fontSize: 12,
                                                color: Colors.white,
                                                fontWeight: FontWeight.bold),
                                          );
                                        }).toList(),
                                        sectionsSpace: 2,
                                      ),
                                    ),
                                  ),
                                  const SizedBox(height: 16),
                                  ...report.categories.map((cat) {
                                    final i = report.categories.indexOf(cat);
                                    return ListTile(
                                      leading: CircleAvatar(
                                        backgroundColor: [
                                          Colors.blue,
                                          Colors.red,
                                          Colors.green,
                                          Colors.orange,
                                          Colors.purple,
                                          Colors.teal,
                                          Colors.pink,
                                          Colors.amber,
                                          Colors.cyan,
                                          Colors.indigo,
                                        ][i % 10],
                                        radius: 8,
                                      ),
                                      title: Text(cat.categoryName),
                                      trailing: Text(
                                        NumberFormat.currency(
                                                symbol: 'PKR ', decimalDigits: 0)
                                            .format(cat.total),
                                        style: const TextStyle(
                                            fontWeight: FontWeight.bold),
                                      ),
                                    );
                                  }),
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
