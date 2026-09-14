import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/budget_model.dart';
import '../services/budget_service.dart';

final budgetServiceProvider = Provider((ref) => BudgetService());

class BudgetState {
  final List<BudgetModel> budgets;
  final List<AlertModel> alerts;
  final bool isLoading;
  final String? error;

  const BudgetState({
    this.budgets = const [],
    this.alerts = const [],
    this.isLoading = false,
    this.error,
  });

  BudgetState copyWith({
    List<BudgetModel>? budgets,
    List<AlertModel>? alerts,
    bool? isLoading,
    String? error,
  }) {
    return BudgetState(
      budgets: budgets ?? this.budgets,
      alerts: alerts ?? this.alerts,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class BudgetNotifier extends Notifier<BudgetState> {
  late final BudgetService _service;

  @override
  BudgetState build() {
    _service = ref.watch(budgetServiceProvider);
    return const BudgetState();
  }

  Future<void> loadBudgets({int? month, int? year}) async {
    state = state.copyWith(isLoading: true);
    try {
      final list = await _service.listBudgets(month: month, year: year);
      state = state.copyWith(budgets: list, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> loadAlerts({int? month, int? year}) async {
    try {
      final alerts = await _service.checkAllAlerts(month: month, year: year);
      state = state.copyWith(alerts: alerts);
    } catch (_) {
      // silently ignore - alerts are supplementary
    }
  }

  Future<void> setBudget(Map<String, dynamic> data) async {
    state = state.copyWith(isLoading: true);
    try {
      await _service.setBudget(data);
      await loadBudgets(month: data['month'] as int?, year: data['year'] as int?);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> updateBudget(int id, {double? amount, double? alertThreshold}) async {
    state = state.copyWith(isLoading: true);
    try {
      await _service.updateBudget(id, amount: amount, alertThreshold: alertThreshold);
      await loadBudgets();
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }
}

final budgetProvider =
    NotifierProvider<BudgetNotifier, BudgetState>(BudgetNotifier.new);
