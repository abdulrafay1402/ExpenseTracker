import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/report_model.dart';
import '../services/report_service.dart';

final reportServiceProvider = Provider((ref) => ReportService());

class ReportState {
  final DashboardModel? dashboard;
  final CategoryWiseReport? categoryWise;
  final MonthlyTrendReport? monthlyTrend;
  final IncomeVsExpenseReport? incomeVsExpense;
  final MonthlySummary? monthlySummary;
  final bool isLoading;
  final String? error;

  const ReportState({
    this.dashboard,
    this.categoryWise,
    this.monthlyTrend,
    this.incomeVsExpense,
    this.monthlySummary,
    this.isLoading = false,
    this.error,
  });

  ReportState copyWith({
    DashboardModel? dashboard,
    CategoryWiseReport? categoryWise,
    MonthlyTrendReport? monthlyTrend,
    IncomeVsExpenseReport? incomeVsExpense,
    MonthlySummary? monthlySummary,
    bool? isLoading,
    String? error,
  }) {
    return ReportState(
      dashboard: dashboard ?? this.dashboard,
      categoryWise: categoryWise ?? this.categoryWise,
      monthlyTrend: monthlyTrend ?? this.monthlyTrend,
      incomeVsExpense: incomeVsExpense ?? this.incomeVsExpense,
      monthlySummary: monthlySummary ?? this.monthlySummary,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class ReportNotifier extends Notifier<ReportState> {
  late final ReportService _service;

  @override
  ReportState build() {
    _service = ref.watch(reportServiceProvider);
    return const ReportState();
  }

  Future<void> loadDashboard({int? month, int? year}) async {
    state = state.copyWith(isLoading: true);
    try {
      final data = await _service.getDashboard(month: month, year: year);
      state = state.copyWith(dashboard: data, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> loadCategoryWise({int? month, int? year}) async {
    state = state.copyWith(isLoading: true);
    try {
      final data = await _service.getCategoryWise(month: month, year: year);
      state = state.copyWith(categoryWise: data, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> loadMonthlyTrend({int? year}) async {
    state = state.copyWith(isLoading: true);
    try {
      final data = await _service.getMonthlyTrend(year: year);
      state = state.copyWith(monthlyTrend: data, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> loadIncomeVsExpense({int? year}) async {
    state = state.copyWith(isLoading: true);
    try {
      final data = await _service.getIncomeVsExpense(year: year);
      state = state.copyWith(incomeVsExpense: data, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> loadMonthlySummary({int? month, int? year}) async {
    state = state.copyWith(isLoading: true);
    try {
      final data = await _service.getMonthlySummary(month: month, year: year);
      state = state.copyWith(monthlySummary: data, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }
}

final reportProvider =
    NotifierProvider<ReportNotifier, ReportState>(ReportNotifier.new);
